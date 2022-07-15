import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]

async def add_tvseries_filter(name, language, quality, seasonlink): 
    mycol = mydb["tvseries"]
    mydict = { "name": str(name), "language": str(language),"quality": str(quality), "seasonlink": str(seasonlink) }
    
    try:
        mycol.insert_one(mydict)
    except:
        logger.exception('Some error occured!', exc_info=True)

async def update_tvseries_filter(name, language, quality, seasonlink):
    mycol = mydb["tvseries"]
    filter = { 'name': str(name) }
    newvalues = { "$set": { "language": str(language), "quality": str(quality), "seasonlink": str(seasonlink) } }
    try:
        mycol.update_one(filter, newvalues)
    except:
        logger.exception('Some error occured!', exc_info=True)

async def remove_tvseries(name):
    mycol = mydb["tvseries"]
    myquery = { 'name': str(name) }
    mycol.delete_one(myquery)
    
async def getlinks():
    mycol = mydb["tvseries"]
    list = []
    for x in mycol.find():
        list.append(x)
    return list
# async def getlinks(name):
#     mycol = mydb["tvseries"]
#     for x in mycol.find({},{ "_id": 0, "name": 1, "language": 1, "quality": 1,"seasonlink": 1}):
#         return x  

async def find_tvseries_filter(name): 
    mycol = mydb["tvseries"]
    list = []
    for x in mycol.find({"name": {$regex : /str(name)/i}}):
        list.append(x)
    return list
#     myquery = { "name": str(name) }
#     myquery = { "name": { "$regex": str(name) } } 
#     mydoc = mycol.find(myquery)
#     for x in mydoc:
#         return x

# https://www.w3schools.com/python/python_mongodb_query.asp
