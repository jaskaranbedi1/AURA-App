import datetime as dt
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from models import JournalEntry

# Connects to a MongoDB Atlas database and returns the client + collection
def connect_to_mongo(mongo_url, db_name, coll_name):
    client = MongoClient(mongo_url)
    db = client[db_name] #select db
    coll = db[coll_name] #select collection
    return client, coll

# save a journal entry into MongoDB
def insert_entry(coll, entry: JournalEntry):

# Convert the JournalEntry object into a dictionary for MongoDB.
    doc = {
        "timestamp": entry.timestamp,
        "text": entry.text,
        "sentiment_label": entry.sentiment_label,
        "sentiment_score": entry.sentiment_score,
        "tag": entry.tag
    }

    result = coll.insert_one(doc)
    return result.inserted_id

# get single entry by mongodb id
def fetch_entry(coll, entry_id):
    return coll.find_one({"_id": entry_id}, {"_id": 0})

# return total number of documents
def count_entries(coll):
    return coll.count_documents({})

# return all journal entries, newest to oldest
def list_entries(coll):
    return list(coll.find().sort("timestamp", -1))

# Return entries matching a specific sentiment (positive/neutral/negative).
def find_by_sentiment(coll, label):
    return list(
        coll.find({"sentiment_label": label}).sort("timestamp", -1)
    )

# Find entries that contain a keyword or phrase 
def find_by_keyword(coll, phrase: str):
    return list(
        coll.find(
            {"text": {"$regex": phrase, "$options": "i"}}
        ).sort("timestamp", -1)
    )

# delete an entry by id. Returns 1 if successful, 0 if not found.
def delete_entry(coll, entry_id):
    result = coll.delete_one({"_id": entry_id})
    return result.deleted_count

