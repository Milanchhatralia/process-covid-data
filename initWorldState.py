import json
import pymongo
import re
import math
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

# Collecting all state objects
allStates = []

# Keep track of all states added from trackcorona.live
worldStateAdded = []

print("##### Fetching data from "+cs+"trackcorona.live/api/provinces"+ce+"...")
req = Request('https://www.trackcorona.live/api/provinces', headers={'User-Agent': 'Mozilla/5.0','Content-Type': 'application/json'})
statesData = json.loads(urlopen(req).read())
statesData = statesData['data']
if statesData:
    print("##### Got data from "+cs+"trackcorona.live/api/provinces"+ce+" as collection")
    pass

# today = date.today()

# Get countryCode to country mapping JSON file
with open('./mapping/countryCode-country.json','r') as countryMappingJSON:
    countryMapping = json.load(countryMappingJSON)

for state in statesData:
    if state['country_code'] != 'in':
        stateData = {
            'state': state['location'],
            'countrycode': state['country_code'].upper(),
            'country': countryMapping[state['country_code'].upper()],
            'latitude': state['latitude'],
            'longitude': state['longitude'],
            'confirmed': state['confirmed'],
            'recovered': state['recovered'],
            'deaths': state['dead'],
            'updated': state['updated'][:19],
            'type': 'state'
        }
        
        
        worldStateAdded.append(stateData['state'])
        # stateCollection.insert_one(stateData)
        allStates.append(stateData)
        # print("State: "+stateData['state'])
        pass
    pass

print("##### Data from "+cs+"trackcorona.live/api/provinces"+ce+" is pushed to collection")
  

# Get all v3 data from covid19India
with urlopen("https://api.covid19india.org/v3/data.json") as c19Iv3DataURI:
    print("##### Got all state meta for "+cs+"India"+ce)
    c19Iv3Data = json.loads(c19Iv3DataURI.read().decode())
    
# Get all active case for respective state
with urlopen("https://api.covid19india.org/data.json") as c19IDataURI:
    print("##### Got all active cases of resp. state of "+cs+"India"+ce)
    c19IData = json.loads(c19IDataURI.read().decode())
    c19IData = c19IData["statewise"]

# Get stateCode to state mapping JSON file
with open('./mapping/stateCode-state.json','r') as stateMappingJSON:
    stateMapping = json.load(stateMappingJSON)

for v3StateCode, v3StateData in c19Iv3Data.items():
    stateData = {
        'statecode': v3StateCode,
        'state': stateMapping[v3StateCode],
        'type': 'state',
        'countrycode': 'IN',
        'country': 'India',
    }
    # Active Cases
    c19IDataState = list(filter(lambda state: state['statecode'] == v3StateCode, c19IData))
    if c19IDataState:
        stateData['active'] = int(c19IDataState[0]['active'])
        pass
    
    # Population
    if 'meta' in v3StateData and 'population' in v3StateData['meta']:
        stateData['population'] = v3StateData['meta']['population']
        pass
    
    # Current data
    if 'total' in v3StateData:
        for key,value in v3StateData['total'].items():
            stateData[key] = value
            pass
        pass
    
    # Delta data
    if 'delta' in v3StateData:
        for key,value in v3StateData['delta'].items():
            stateData['delta'+key] = value
            pass
        pass
    
    # Manual reconciliation
    if 'tested' in stateData and 'population' in stateData:
        stateData['testpermillion'] = math.trunc( ( stateData['tested'] / stateData['population'] ) * 1000000 )
        stateData['testperthousand'] =  math.trunc( ( stateData['tested'] / stateData['population'] ) * 1000 )
        pass
    
    allStates.append(stateData)
    pass


print("##### All "+cs+"Indian"+ce+" states are added to collection")


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
                'countrycode': item['stateId'][5:7].upper(),
                'country': countryMapping[item['stateId'][5:7].upper()],
                'latitude': item['coordinates'][0],
                'longitude': item['coordinates'][1],
                'type': 'state',
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
            allStates.append(stateData)
            # stateCollection.insert_one(stateData)
            # print("State: "+stateData['state'])
            pass
        pass
    
    # elif item['level'] == 'county':
    #     if '-' in item['countyId']:
    #         countyID = str(item['countyId'][item['countyId'].index('-')+1:].strip()),
    #         pass
    #     elif ':' in item['countyId']:
    #         countyID = str(item['countyId'][item['countyId'].index(':')+1:].strip()),
    #         pass
    #     countyData = {
    #         'county': item['county'],
    #         'country': item['country'],
    #         'countycode': countyID,
    #         'statecode': item['stateId'][8:].strip(),
    #         'countrycode': item['stateId'][5:7],
    #         'latitude': item['coordinates'][0],
    #         'longitude': item['coordinates'][1]
    #     }
    #     if 'deaths' in item:
    #         countyData['deaths'] = item['deaths']
    #         pass
    #     if 'cases' in item:
    #         countyData['confirmed'] = item['cases']
    #         pass
    #     if 'hospitalized' in item:
    #         countyData['active'] = item['hospitalized']
    #         pass
    #     if 'active' in item:
    #         countyData['active'] = item['active']
    #         pass
    #     if 'discharged' in item:
    #         countyData['recovered'] = item['discharged']
    #         pass
    #     if 'recovered' in item:
    #         countyData['recovered'] = item['recovered']
    #         pass
    #     allStates.append(countyData)
    #     # stateCollection.insert_one(countyData)
    #     # print("County: "+countyData['county'])
    #     pass
    pass

# Delete all documents from state test collection
delete = stateCollection.delete_many({})
print("##### Cleared all "+ cs + str(delete.deleted_count) + ce +" documents from "+ cs + str(stateCollection.name + ce))

# Moving all documents to state test collection
stateCollection.insert_many(allStates)
print("##### Moved all "+ cs + str(len(allStates)) + ce +" documents to "+ cs + str(stateCollection.name) + ce)

# Delete all documents from state main collection
delete = mainCollection.delete_many({})
print("##### Cleared all "+ cs + str(delete.deleted_count) + ce+" documents from "+ cs + str(mainCollection.name) + ce)

# Moving all documents to state main collection
mainCollection.insert_many(allStates)
print("##### Moved all "+ cs + str(len(allStates)) + ce +" documents to "+ cs + str(mainCollection.name) + ce)

print("##### "+cs+"Done bro"+ce+", check new collection")