import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_notification(userId, stats):
    mycol = mydb["notification"]
    mydict = {"userId": str(userId), "stats": str(stats)}

    try:
        mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def update_notification(userId, stats):
    mycol = mydb["notification"]
    filter = {'userId': str(userId)}
    newvalues = {"$set": {"stats": str(stats)}}
    try:
        mycol.update_one(filter, newvalues)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def remove_notification(userId):
    mycol = mydb["notification"]
    myquery = {'userId': str(userId)}
    mycol.delete_one(myquery)


async def find_allusers():
    mycol = mydb["notification"]
    list = []
    for x in mycol.find():
        list.append(x["userId"])
    return list


async def find_notification(userId):
    mycol = mydb["notification"]
    myquery = {"userId": str(userId)}
    mydoc = mycol.find(myquery)
    for x in mydoc:
        return x
