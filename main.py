import os
from dotenv import load_dotenv
from sentiment import HuggingFaceSentimentStrategy
from db import (
    connect_to_mongo,
    insert_entry,
    list_entries
)
from factory import EntryFactory
from decorators import TaggingDecorator

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
            # Extract fields safely
            entry_number = total - i + 1
            text = doc.get("text", "")
            sentiment = doc.get("sentiment_label")
            score = doc.get("sentiment_score")
            tag = doc.get("tag") 
            ts = doc.get("timestamp")

            # Shorten timestamp formatting
            ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)

            # Print entry
            print(f"\nEntry #{entry_number} ({ts_str})")

            print(f"  Text: {text}")

            if sentiment:
                pct = round(score * 100, 2)
                print(f"  Sentiment: {sentiment} ({pct}%)")

            if tag:
                print(f"  Tag: {tag}")

    finally:
        client.close()


def main():
    print("=== AURA AI-Powered Journeling App ===")

    # Load env variables
    mongo_url, db_name, coll_name, hf_token = load_config()


    # Initialize Hugging Face client 
    sentiment_strategy = HuggingFaceSentimentStrategy(hf_token)

    while True:
        print("\n=== AURA Journaling CLI ===")
        print("1) Add new entry")
        print("2) View all entries")
        print("3) Quit")

        choice = input("Choose an option: ").strip()
    
        if choice == "1":
            add_entry_flow(sentiment_strategy, mongo_url, db_name, coll_name)
        elif choice == "2":
            list_entries_flow(mongo_url, db_name, coll_name)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()