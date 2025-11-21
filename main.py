import os
import datetime as dt
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from huggingface_hub import InferenceClient


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


def main():
    
    # Load configuration
    mongo_url, db_name, coll_name, hf_token = load_config()

    # Initialize Hugging Face client 
    hf_client = InferenceClient(api_key=hf_token)

    # Ask user for some text to analyze
    print("=== AURA Journelling App ===")
    user_text = input("Enter a short journal sentence to analyze:\n> ").strip()
    if not user_text:
        print("No text entered, exiting.")
        return


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
    client = MongoClient(mongo_url, tls=True, tlsAllowInvalidCertificates=False)
    db = client[db_name]
    coll = db[coll_name]


    # build document
    doc = {
        "timestamp": dt.datetime.utcnow(),
        "text": user_text,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score
    }

    # insert into mongo
    try:
        ins = coll.insert_one(doc)
        print(f"\nInserted document with _id: {ins.inserted_id}")

        # Read it back
        found = coll.find_one({"_id": ins.inserted_id}, {"_id": 0})
        print("Fetched document from MongoDB:")
        print(found)

        # Count how many docs exist now
        total = coll.count_documents({})
        print(f"Total documents in '{coll_name}': {total}")

    except PyMongoError as e:
        print("MongoDB error:", e)
    finally:
        client.close()

if __name__ == "__main__":
    main()
