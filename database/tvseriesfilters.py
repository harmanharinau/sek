import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_tvseries_filter(name, language, quality, seasonlink):
    mycol = mydb["tvseries"]
    mydict = {"name": str(name), "language": str(
        language), "quality": str(quality), "seasonlink": str(seasonlink)}

    try:
        mycol.insert_one(mydict)
    except Exception:
        logger.exception('Some error occured!', exc_info=True)


async def update_tvseries_filter(name, language, quality, seasonlink):
    mycol = mydb["tvseries"]
    filter = {'name': str(name)}
    newvalues = {"$set": {"language": str(language), "quality": str(
        quality), "seasonlink": str(seasonlink)}}

    try:
        mycol.update_one(filter, newvalues)
    except Exception:
        logger.exception('Some error occured!', exc_info=True)


async def remove_tvseries(name):
    mycol = mydb["tvseries"]
    myquery = {'name': str(name)}
    mycol.delete_one(myquery)


async def getlinks():
    mycol = mydb["tvseries"]
    return list(mycol.find())


async def find_tvseries_filter(name):
    mycol = mydb["tvseries"]
    return list(mycol.find({'name': {'$regex': f'{name}'}}))


async def find_tvseries_by_first(letter):
    mycol = mydb["tvseries"]
    return list(mycol.find({'name': {'$regex': f'^{letter}'}}))

# https://www.w3schools.com/python/python_mongodb_query.asp
