import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_inst_filter(fileid, links):
    mycol = mydb["quickdb"]
    mydict = {"fileid": str(fileid), "links": str(links)}

    try:
        x = mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def remove_inst(fileid):
    mycol = mydb["quickdb"]
    myquery = {"fileid": str(fileid)}
    mycol.delete_one(myquery)


async def get_ids(fileid):
    mycol = mydb["quickdb"]
    myquery = {"fileid": str(fileid)}
    mydoc = mycol.find(myquery)
    for x in mydoc:
        return x


async def get(id):
    mycol = mydb["quickdb"]
    for x in mycol.find():
        return x


async def add_sent_files(userid, fileid):
    mycol = mydb["sentfiledb"]
    mydict = {"fileid": str(fileid), "userid": str(userid)}

    try:
        x = mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def count_sent_files():
    mycol = mydb["sentfiledb"]
    files = mycol.count()

    return files


async def add_verification(user_id, stats, file_id, updat_time):
    mycol = mydb["verification"]
    mydict = {"userId": str(user_id), "stats": str(
        stats), "file": str(file_id), "updat_time": str(updat_time)}

    try:
        x = mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def remove_verification(user_id):
    mycol = mydb["verification"]
    myquery = {"userId": str(user_id)}
    mycol.delete_one(myquery)


async def get_verification(user_id):
    mycol = mydb["verification"]
    myquery = {"userId": str(user_id)}
    mydoc = mycol.find(myquery)
    for user_dic in mydoc:
        return user_dic
