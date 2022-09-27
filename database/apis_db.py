import pymongo
from config import Config 

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DATABASE_URI = Config.DATABASE_URI
DATABASE_NAME = Config.DATABASE_NAME

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]

async def add_api(chat_id, api):
    mycol = mydb["usersapites"]
    mydict = { "userid": str(chat_id), "userapi": str(api) }
    
    try:
        mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)
        
async def update_api(chat_id, api):
    mycol = mydb["usersapites"]
    filter = { 'userid': str(chat_id) }
    newvalues = { "$set": { 'userapi': str(api) } }
    mycol.update_one(filter, newvalues)  

async def find_api(chat_id):
    mycol = mydb["usersapites"]
    myquery = { "userid": str(chat_id) }
    mydoc = mycol.find(myquery)
    for x in mydoc:
        return 
