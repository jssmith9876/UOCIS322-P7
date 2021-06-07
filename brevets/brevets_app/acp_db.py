from pymongo import MongoClient
import os

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetdb

def clear_table():
    db.brevetdb.drop()

def insert_time(time):
    # Error handling to see if the insertion fails
    try:
        db.brevetdb.insert_one(time)
        return True
    except Exception as e:
        return False

def get_times():
    return list(db.brevetdb.find())