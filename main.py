import os
from dotenv import load_dotenv
from sentiment import HuggingFaceSentimentStrategy, CachingSentimentProxy
from db import (
    connect_to_mongo,
    insert_entry,
    list_entries,
    find_by_sentiment,
    find_by_keyword,
    delete_entry
)
from factory import EntryFactory
from decoratorx import TaggingDecorator

# Load configuration from .env and return the values we need.
def load_config():

    load_dotenv()

    mongo_url = os.getenv("MONGODB_URL")
    db_name = os.getenv("DB_NAME", "aura")
    coll_name = os.getenv("COLLECTION", "entries")
    hf_token = os.getenv("HF_TOKEN")

    if not mongo_url:
        raise SystemExit("MONGODB_URL is missing in .env")

    if not hf_token:
        raise SystemExit("HF_TOKEN is missing in .env")

    return mongo_url, db_name, coll_name, hf_token


# Prompt user for text, analyze sentiment, save entry to MongoDB.
def add_entry_flow(sentiment_strategy, mongo_url, db_name, coll_name):
    print("\n--- Add new journal entry ---")
    user_text = input("Write your entry:\n> ").strip()

    if not user_text:
        print("No text entered. Returning to menu.")
        return
    
    # Call sentiment analysis strategy and handle API errors
    try:
        sentiment_label, sentiment_score = sentiment_strategy.get_sentiment(user_text)
        print("\nSentiment result:")
        print(f"{sentiment_label.capitalize()}: {round(sentiment_score * 100, 2)}%")
    except Exception as e:
        print(f"Error calling Hugging Face API: {e}")
        sentiment_label = None
        sentiment_score = None

    # Build a JournalEntry object
    entry = EntryFactory.create(
        text=user_text,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score
    )

    # Decorator Pattern: add a mood tag based on sentiment
    entry = TaggingDecorator(entry).add_tag()

    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entry_id = insert_entry(coll, entry)
        print(f"\nSaved entry with _id: {entry_id}")
    finally:
        client.close()


#helper function to print a single journal entry in a consistent format
def print_entry(doc, index=None):

    text = doc.get("text", "")
    sentiment = doc.get("sentiment_label")
    score = doc.get("sentiment_score")
    tag = doc.get("tag")
    ts = doc.get("timestamp")

    # Format timestamp
    ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)

    # Print entry
    if index is not None:
        print(f"\nEntry #{index} ({ts_str})")
    else:
        print(f"\n({ts_str})")

    # Print fields
    if tag:
        print(f"  Tag: {tag}")

    if sentiment:
        pct = round(score * 100, 2)
        print(f"  Sentiment: {sentiment} ({pct}%)")

    print(f"  Text: {text}")


#list all entries
def list_entries_flow(mongo_url, db_name, coll_name):
    print("\n--- Your journal entries ---")
    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entries = list_entries(coll)

        if not entries:
            print("No entries found.")
            return

        total = len(entries)

        print(f"Total entries: {total}")
              
        for i, doc in enumerate(entries, start=1):
            #calling print_entry() to print
            print_entry(doc, i)

    finally:
        client.close()


#filter search based on sentiment
def find_by_sentiment_flow(mongo_url, db_name, coll_name):
    print("\n--- Search entries by sentiment ---")
    label = input("Enter sentiment (positive / neutral / negative): ").strip().lower()

    if label not in {"positive", "neutral", "negative"}:
        print("Invalid sentiment. Please enter: positive, neutral, or negative.")
        return

    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entries = find_by_sentiment(coll, label)

        if not entries:
            print(f"No entries found with sentiment: {label}")
            return

        total = len(entries)
        print(f"Found {total} entries with sentiment '{label}':")

        for i, doc in enumerate(entries, start=1):
            #calling print_entry() to print
            print_entry(doc, i)
    finally:
        client.close()


#filter search based on keyword/phrase
def find_by_keyword_flow(mongo_url, db_name, coll_name):
    print("\n--- Search entries by keyword or phrase ---")
    phrase = input("Enter a keyword or phrase to search for (e.g., 'life', 'life is good', 'feeling stressed'):\n> ").strip()

    if not phrase:
        print("No keyword/phrase entered. Returning to menu.")
        return

    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entries = find_by_keyword(coll, phrase)

        if not entries:
            print(f"No entries found containing: '{phrase}'")
            return

        print(f"Found {len(entries)} entries containing '{phrase}':")

        for i, doc in enumerate(entries, start=1):
            print_entry(doc, i)

    finally:
        client.close()


#delete an entry
def delete_entry_flow(mongo_url, db_name, coll_name):
    print("\n--- Delete a journal entry ---")
    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entries = list_entries(coll)

        if not entries:
            print("No entries found to delete.")
            return

        print(f"Total entries: {len(entries)}")

        # Show entries with index
        for i, doc in enumerate(entries, start=1):
            _id = doc.get("_id")
            print_entry(doc, i)
           
        choice = input("\nEnter the entry number you want to delete (or press Enter to cancel): ").strip()
        if not choice:
            print("Delete cancelled.")
            return

        if not choice.isdigit():
            print("Invalid number.")
            return

        idx = int(choice)
        if idx < 1 or idx > len(entries):
            print("Number out of range.")
            return

        # Get selected document
        doc = entries[idx - 1]
        _id = doc.get("_id")

        print("\nYou chose to delete this entry:")
        print_entry(doc, idx)

        confirm = input("\nAre you sure you want to delete this entry? (y/n): ").strip().lower()
        if confirm != "y":
            print("Delete cancelled.")
            return

        deleted = delete_entry(coll, _id)
        if deleted == 1:
            print("Entry deleted successfully.")
        else:
            print("Delete failed. Entry may not exist anymore.")

    finally:
        client.close()


# generate a report showing mood stats
def mood_report_flow(mongo_url, db_name, coll_name):
    print("\n--- Mood Summary Report ---")
    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)

    try:
        entries = list_entries(coll)

        if not entries:
            print("No journal entries found.")
            return

        total = len(entries)

        # Count labels
        pos = sum(1 for doc in entries if doc.get("sentiment_label") == "positive")
        neu = sum(1 for doc in entries if doc.get("sentiment_label") == "neutral")
        neg = sum(1 for doc in entries if doc.get("sentiment_label") == "negative")

        scores = []

        for e in entries:
            score = e.get("sentiment_score")
            if score is not None:
                scores.append(score)

        # Compute average score (if any scores exist)
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Find most common mood
        mood_counts = {
            "positive": pos,
            "neutral": neu,
            "negative": neg,
        }
        most_common = max(mood_counts, key=mood_counts.get)

        print(f"Total entries: {total}")
        print(f"Positive: {pos}")
        print(f"Neutral: {neu}")
        print(f"Negative: {neg}")
        print(f"\nMost common mood: {most_common.capitalize()}")
        print(f"Average sentiment score: {avg_score:.2f}")

    finally:
        client.close()


def main():
    print("=== AURA AI-Powered Journeling App ===")

    # Load env variables
    mongo_url, db_name, coll_name, hf_token = load_config()


    # Initialize Hugging Face strategy and wrap it with Proxy for caching
    base_strategy = HuggingFaceSentimentStrategy(hf_token)
    sentiment_strategy = CachingSentimentProxy(base_strategy)

    while True:
        print("\n=== AURA Journaling CLI ===")
        print("1) Add new entry")
        print("2) View all entries")
        print("3) Search entries by sentiment")
        print("4) Search entries by phrase")
        print("5) Delete an entry")
        print("6) Mood report")
        print("7) Quit")

        choice = input("Choose an option: ").strip()
    
        if choice == "1":
            add_entry_flow(sentiment_strategy, mongo_url, db_name, coll_name)
        elif choice == "2":
            list_entries_flow(mongo_url, db_name, coll_name)
        elif choice == "3":
            find_by_sentiment_flow(mongo_url, db_name, coll_name)
        elif choice == "4":
            find_by_keyword_flow(mongo_url, db_name, coll_name)
        elif choice == "5":
            delete_entry_flow(mongo_url, db_name, coll_name)
        elif choice == "6":
            mood_report_flow(mongo_url, db_name, coll_name)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")

if __name__ == "__main__":
    main()