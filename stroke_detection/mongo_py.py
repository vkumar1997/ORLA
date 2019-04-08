import pymongo

myclient = pymongo.MongoClient("mongodb+srv://vikas:a221sector122@cluster0-gbitb.gcp.mongodb.net/test?retryWrites=true")
print(myclient.database_names())