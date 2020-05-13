import json
import pymongo
import re
# import urllib.request as covidURL

from urllib.request import Request, urlopen

# Import Date time
# from datetime import datetime
# from datetime import date

######### MAKE SURE TO DOWNLOAD BEFORE RUNNNING
# https://coronadatascraper.com/#data.json -----> data.json

cs = "\033[32m"
ce = "\033[0m"

client = pymongo.MongoClient("mongodb+srv://write-covid-live:covid-write-3214@urja-lvfxu.mongodb.net/test?retryWrites=true&w=majority")
db = client['covid-live']
stateCollection = db['state-test']
mainCollection = db['state-main']

delete = stateCollection.delete_many({})
print("##### "+ cs + str(delete.deleted_count) + ce +" Documents deleted from "+ cs + str(stateCollection.name + ce))


req = Request('https://www.trackcorona.live/api/provinces', headers={'User-Agent': 'Mozilla/5.0','Content-Type': 'application/json'})
allStates = json.loads(urlopen(req).read())
allStates = allStates['data']
if allStates:
    print("##### Got data from "+cs+"trackcorona.live/api/provinces"+ce+" as collection")
    pass

worldStateAdded = []

# print(data[0]['level'])

# today = date.today()

for state in allStates:
    if state['country_code'] != 'in':
        stateData = {
            'state': state['location'],
            'countrycode': state['country_code'],
            'latitude': state['latitude'],
            'longitude': state['longitude'],
            'confirmed': state['confirmed'],
            'recovered': state['recovered'],
            'deaths': state['dead'],
            'updated': state['updated'][:19]
        }
        
        # if 'updated' in state:
        #     stateData['updated'] = state['updated'][:19]
        #     dataDate = datetime.strptime(stateData['updated'], '%Y-%m-%d %H:%M:%S').date()
        #     notUpdatedStates.append(stateData['state'])
        #     pass
        worldStateAdded.append(stateData['state'])
        stateCollection.insert_one(stateData)
        print("State: "+stateData['state'])
        pass
    pass

print("##### Data from "+cs+"trackcorona.live/api/provinces"+ce+" is pushed to collection")


# For indian states
with urlopen("https://api.covid19india.org/data.json") as indiaStates:
    print("##### Got collection of all states in "+cs+"India"+ce)
    indiaState = json.loads(indiaStates.read().decode())
    indiaState = indiaState['statewise']
    
with urlopen("https://api.covid19india.org/resources/resources.json") as resourceURL:
    print("##### Got all resources for "+cs+"India"+ce)
    allResources = json.loads(resourceURL.read().decode())
    allResources = allResources['resources']
    

for state in indiaState:
    resourceArr = []
    for resource in allResources:
        if resource['state'] == state['state']:
            resourceArr.append(resource)
            pass
        pass
    stateData = state
    stateData['resources'] = resourceArr
    stateCollection.insert_one(stateData)
    print("State: "+stateData['state'])
    pass

print("##### All "+cs+"Indian"+ce+" states are pushed to collection")


# For remaining state which are not in above API

# file = open('data.json', 'r')
# data = json.loads(file.read())

req = Request('https://coronadatascraper.com/data.json', headers={'User-Agent': 'Mozilla/5.0','Content-Type': 'application/json'})
data = json.loads(urlopen(req).read())
if data:
    print("##### Got data from "+cs+"https://coronadatascraper.com"+ce+" as collection")
    pass


remainStates = []
print("##### Pushing states and county from "+cs+"coronadatascraper.com"+ce)

for item in data:
    if item['level'] == 'state':
        # remainStates.append(item)
        present = False
        searchState = item['state'].strip()
        r = re.compile(" ?"+searchState+" ?")
        if list(filter(r.match, worldStateAdded)):
            present = True
            pass
        
        if not present and item['countryId'][5:] not in 'IN':
            stateData = {
                'state': item['state'],
                'country': item['country'],
                'statecode': item['stateId'][8:].strip(),
                'countrycode': item['stateId'][5:7],
                'latitude': item['coordinates'][0],
                'longitude': item['coordinates'][1]
            }
            if 'deaths' in item:
                stateData['deaths'] = item['deaths']
                pass
            if 'cases' in item:
                stateData['confirmed'] = item['cases']
                pass
            if 'hospitalized' in item:
                stateData['active'] = item['hospitalized']
                pass
            if 'active' in item:
                stateData['active'] = item['active']
                pass
            if 'discharged' in item:
                stateData['recovered'] = item['discharged']
                pass
            if 'recovered' in item:
                stateData['recovered'] = item['recovered']
                pass
            stateCollection.insert_one(stateData)
            print("State: "+stateData['state'])
            pass
        pass
    
    elif item['level'] == 'county':
        if '-' in item['countyId']:
            countyID = str(item['countyId'][item['countyId'].index('-')+1:].strip()),
            pass
        elif ':' in item['countyId']:
            countyID = str(item['countyId'][item['countyId'].index(':')+1:].strip()),
            pass
        countyData = {
            'county': item['county'],
            'country': item['country'],
            'countycode': countyID,
            'statecode': item['stateId'][8:].strip(),
            'countrycode': item['stateId'][5:7],
            'latitude': item['coordinates'][0],
            'longitude': item['coordinates'][1]
        }
        if 'deaths' in item:
            countyData['deaths'] = item['deaths']
            pass
        if 'cases' in item:
            countyData['confirmed'] = item['cases']
            pass
        if 'hospitalized' in item:
            countyData['active'] = item['hospitalized']
            pass
        if 'active' in item:
            countyData['active'] = item['active']
            pass
        if 'discharged' in item:
            countyData['recovered'] = item['discharged']
            pass
        if 'recovered' in item:
            countyData['recovered'] = item['recovered']
            pass
        stateCollection.insert_one(countyData)
        print("County: "+countyData['county'])
        pass
    pass

# Migrate to main collection
clearMainCol = mainCollection.delete_many({})
print("##### Cleared all "+ cs + str(clearMainCol.deleted_count) + ce+" documents from "+ cs + str(mainCollection.name) + ce)

# Get all document from collection to copy from
dataToMigrate = stateCollection.find({})
print("##### "+ cs + str(stateCollection.count_documents({})) + ce +" Documents will migrate from "+cs + str(stateCollection.name) + ce +" to "+ cs + str(mainCollection.name) + ce)

#Copying all document to collection
dataMove = mainCollection.insert_many(dataToMigrate)
print("##### Migrated "+ cs + str(stateCollection.count_documents({})) + ce +" document from "+ cs + str(stateCollection.name) + ce +" to "+ cs + str(mainCollection.name) + ce)
print("##### "+cs+"Done bro"+ce+", check new collection")