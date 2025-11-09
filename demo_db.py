import os
import datetime as dt
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

def main():
    # Load secrets from .env 
    load_dotenv()
    uri = os.environ["MONGODB_URI"]       
    db_name = os.getenv("DB_NAME", "aura")
    coll_name = os.getenv("COLLECTION", "entries")

    # Connect to MongoDB Atlas 
    client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=False)
    db = client[db_name]
    coll = db[coll_name]

    # Insert one tiny document
    doc = {
        "timestamp": dt.datetime.utcnow(),
        "text": "Milestone 2 hello world",
        "sentiment_label": None,
        "sentiment_score": None
    }

    try:
        ins = coll.insert_one(doc)
        print(f"Inserted _id: {ins.inserted_id}")

        # Read it back to prove it worked
        found = coll.find_one({"_id": ins.inserted_id}, {"_id": 0})
        print("Fetched document:", found)

        # Count how many docs exist now
        total = coll.count_documents({})
        print(f"Total documents in '{coll_name}': {total}")

    except PyMongoError as e:
        print("MongoDB error:", e)
    finally:
        client.close()

if __name__ == "__main__":
    main()
