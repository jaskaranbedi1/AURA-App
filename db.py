import datetime as dt
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Connect to MongoDB Atla
def connect_to_mongo(mongo_url, db_name, coll_name):
    client = MongoClient(mongo_url, tls=True, tlsAllowInvalidCertificates=False)
    db = client[db_name]
    coll = db[coll_name]
    return client, coll


# insert a journal entry into MongoDB
def insert_entry(coll, text, sentiment_label, sentiment_score):
    
    # build document
    doc = {
        "timestamp": dt.datetime.now(dt.timezone.utc),
        "text": text,
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
    }

    result = coll.insert_one(doc)
    return result.inserted_id


# fetch entry by its ID (hide _id in output for cleaner CLI)
def fetch_entry(coll, entry_id):
    return coll.find_one({"_id": entry_id}, {"_id": 0})


# returns total number of documents
def count_entries(coll):
    return coll.count_documents({})