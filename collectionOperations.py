import pymongo
import sys

client = pymongo.MongoClient("mongodb+srv://write-covid-live:covid-write-3214@urja-lvfxu.mongodb.net/test?retryWrites=true&w=majority")
db = client["covid-live"]

cs = "\033[32m"
ce = "\033[0m"

action = sys.argv[1][1:]

if action == 'd':
    colToDelete = db[sys.argv[2]]
    delete = colToDelete.delete_many({})
    print("##### "+ cs + str(delete.deleted_count) + ce +" Documents deleted from "+ cs + str(colToDelete.name + ce))
    pass
elif action == 'm':
    fromCol = db[sys.argv[2]]
    toCol = db[sys.argv[3]]
    
    # Clear all document from collection to copy
    clearToCol = toCol.delete_many({})
    print("##### Cleared all "+ cs + str(clearToCol.deleted_count) + ce+" documents from "+ cs + str(toCol.name) + ce)
    
    # Get all document from collection to copy from
    dataToMigrate = fromCol.find({})
    print("##### "+ cs + str(fromCol.count_documents({})) + ce +" Documents will migrate from "+cs + str(fromCol.name) + ce +" to "+ cs + str(toCol.name) + ce)
    
    #Copying all document to collection
    dataMove = toCol.insert_many(dataToMigrate)
    print("##### Migrated "+ cs + str(toCol.count_documents({})) + ce +" document from "+ cs + str(fromCol.name) + ce +" to "+ cs + str(toCol.name) + ce)
    pass


