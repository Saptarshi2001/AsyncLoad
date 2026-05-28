from env import getenv
import pymongo

class Record:

    def __init__(self):
        pass 
       
    def insertpayload(self,kv):  # a key value through which we store it in mongodb.Now we can add as many key value store as we want ,but the collc wodnt care about it. the url endpoint and then the values ,that url endpoint structure should stay intact
        
        env=getenv()
        client=pymongo.MongoClient(env.MONGO_URL)
        db=client[env.DATABASE]
        collc=db[env.COLLECTION]
        
        