import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_sundisk(chat_id, api):
    mycol = mydb["sundisk"]
    mydict = {"chat_id": str(chat_id), "api": str(
        api)}

    try:
        x = mycol.insert_one(mydict)
    except Exception:
        logger.exception('Some error occured!', exc_info=True)


async def remove_sundisk(chat_id):
    mycol = mydb["sundisk"]
    myquery = {"chat_id": str(chat_id)}
    mycol.delete_one(myquery)


async def get_sundisk(chat_id):
    mycol = mydb["sundisk"]
    myquery = {"chat_id": str(chat_id)}
    mydoc = mycol.find(myquery)
    for user_dic in mydoc:
        return user_dic
