import os
from dotenv import load_dotenv
from sentiment import init_hf_client, get_sentiment
from db import (
    connect_to_mongo,
    insert_entry,
    fetch_entry,
    count_entries
)

#Load configuration from .env and return the values we need.
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


def main():

    print("=== AURA Journelling App ===")

    # Ask user for some text to analyze
    user_text = input("Enter a short journal sentence to analyze:\n> ").strip()
    if not user_text:
        print("No text entered, exiting.")
        return


    # Load env variables
    mongo_url, db_name, coll_name, hf_token = load_config()


    # Initialize Hugging Face client 
    hf_client = init_hf_client(hf_token)


    # Call Hugging Face sentiment
    try:
        sentiment_label, sentiment_score = get_sentiment(hf_client, user_text)
        print("\nSentiment result:")
        print(f"{sentiment_label.capitalize()}: {round(sentiment_score * 100, 2)}%")

    except Exception as e:
        print(f"Error calling Hugging Face API: {e}")
        # If API fails, we still want to test Mongo connection, so set None
        sentiment_label = None
        sentiment_score = None

    
    # Connect to MongoDB Atla
    client, coll = connect_to_mongo(mongo_url, db_name, coll_name)
    db = client[db_name]
    coll = db[coll_name]


    # insert into mongo
    try:
        entry_id = insert_entry(coll, user_text, sentiment_label, sentiment_score)
        print(f"\nInserted document with _id: {entry_id}")

        # Fetch entry from database
        fetched = fetch_entry(coll, entry_id)
        print("Fetched document from MongoDB:")
        print(fetched)

        # Count how many docs exist now
        total = count_entries(coll)
        print(f"Total documents in '{coll_name}': {total}")
    finally:
        client.close()

if __name__ == "__main__":
    main()





























# Call Hugging Face sentiment model and mapping labels to negative/neutral/positive
def get_sentiment(client: InferenceClient, text):

    result = client.text_classification(
        text,
        model="cardiffnlp/twitter-roberta-base-sentiment",
        top_k=1
    )

    r = result[0]

    if r.label == "LABEL_0":
        sentiment = "negative"
    elif r.label == "LABEL_1":
        sentiment = "neutral"
    elif r.label == "LABEL_2":
        sentiment = "positive"
    else:
        sentiment = r.label  # fallback, just in case

    return sentiment, float(r.score)


