import pymongo
from pymongo.server_api import ServerApi

class Config:
    VERSION = "A 1.00"
    DRIVE = "G"
    
    // TODO Change the user and password to the match yours
    DATABASE = pymongo.MongoClient("mongodb+srv://USER:PASSWORD@aetherdrive.d6b4m.mongodb.net/Sensor?retryWrites=true&w=majority")
