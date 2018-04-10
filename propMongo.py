import os
from pymongo import MongoClient
import ssl

def connect_to_mongo(col):
    muser = os.environ.get('MONGO_USERNAME')
    mpw = os.environ.get('MONGO_PW')
    url = 'mongodb://{}:{}@hgdb-shard-00-00-fo5jm.mongodb.net:27017, \
    hgdb-shard-00-01-fo5jm.mongodb.net:27017, \
    hgdb-shard-00-02-fo5jm.mongodb.net:27017/test?replicaSet=hgdb-shard-0&authSource=admin'.format(muser,mpw)
    client = MongoClient(url,
        ssl=True,
        ssl_cert_reqs=ssl.CERT_NONE)
    collection = client.housegoals[col]
    return collection

def add_property(d, col):
    collection = connect_to_mongo(col)
    d['_id'] = d['zpid'] # Mongo id == zpid
    status = collection.insert_one(d)
    return status

def find_property(d, col):
    collection = connect_to_mongo(col)
    return collection.find_one({'_id': d['_id']})  

def get_prop_list(col):
    collection = connect_to_mongo(col)
    return [doc for doc in collection.find({})]

if __name__ == "__main__":
    print(get_prop_list('properties'))