
from dataclasses import dataclass
import os

class EnvKeys:
    MONGO_URL='MONGO_URL'
    MONGO_DATABASE='MONGO_DATABASE'
    MONGO_COLLECTION='MONGO_COLLECTION'
    TIMEOUT='TIMEOUT'
    TOTAL_REQUESTS='TOTAL_REQUESTS'
    CONCURRENT_REQUESTS='CONCURRENT_REQUESTS'
    HTTP_METHOD='HTTP_METHOD'

@dataclass
class Env:
    MONGO_URL:str
    DATABASE:str
    COLLECTION:str
    TIMEOUT:int
    TOTAL_REQUESTS:int
    CONCURRENT_REQUESTS:int
    HTTP_METHOD:str

def getenv():
    mongourl = os.getenv(EnvKeys.MONGO_URL)
    database = os.getenv(EnvKeys.MONGO_DATABASE)
    collection_name = os.getenv(EnvKeys.MONGO_COLLECTION)
    timeout=os.getenv(EnvKeys.TIMEOUT)
    total_requests=os.getenv(EnvKeys.TOTAL_REQUESTS)
    concurrent_requests=os.getenv(EnvKeys.CONCURRENT_REQUESTS)
    method=os.getenv(EnvKeys.HTTP_METHOD)

    return Env(mongourl,database,collection_name,timeout,total_requests,concurrent_requests,method)