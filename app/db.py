import pymongo
from config import config


class DB:
    client = pymongo.MongoClient(f"mongodb://localhost:{config.DB_PORT}/")
    db = client["rc_coffee"]

    def __init__(self, collection):
        self.collection = self.db[collection]

    def insert(self, data):
        self.collection.insert_one(data)

    def find(self, query):
        return self.collection.find(query)

    def update(self, query, data):
        self.collection.update_one(query, {"$set": data})

    def exist(self, query):
        return self.collection.find_one(query) is not None

    def delete(self, query):
        self.collection.delete_one(query)
