import pymongo
from pymongo.server_api import ServerApi

class Config:
    VERSION = "A 1.00"
    DRIVE = "G"
    DATABASE = pymongo.MongoClient("mongodb+srv://guyokay:12345@aetherdrive.d6b4m.mongodb.net/Sensor?retryWrites=true&w=majority")