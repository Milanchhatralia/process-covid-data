import json
import pymongo

from urllib.request import Request, urlopen

cs = "\033[32m"
ce = "\033[0m"

client = pymongo.MongoClient("mongodb+srv://write-covid-live:covid-write-3214@urja-lvfxu.mongodb.net/test?retryWrites=true&w=majority")
db = client['covid-live']
cityCollection = db['city-test']
mainCollection = db['city-main']

# Collecting all city data
allCities = []

# Get all cities
print("##### Fetching data from "+cs+"trackcorona.live/api/cities"+ce+"...")
req = Request('https://www.trackcorona.live/api/cities', headers={'User-Agent': 'Mozilla/5.0','Content-Type': 'application/json'})
citiesData = json.loads(urlopen(req).read())
citiesData = citiesData['data']
if citiesData:
    print("##### Got data from "+cs+"trackcorona.live/api/cities"+ce+" as collection")
    pass

for city in citiesData:
    if city['country_code'] not in 'in':
        cityData = {
            'countrycode': city['country_code'],
            'confirmed': city['confirmed'],
            'deaths': city['dead'],
            'recovered': city['recovered'],
            'updated': city['updated'][:19]
        }
        
        if ',' in city['location']:
            cityData['city'] = city['location'].partition(',')[0].strip()
            cityData['state'] = city['location'].partition(',')[2].strip()
            pass
        else:
            cityData['city'] = city['location']
            pass
        
        allCities.append(cityData)
        # cityCollection.insert_one(cityData)
        print("City: "+cityData['city'])
        pass
    pass
print("##### Data from "+cs+"trackcorona.live/api/cities"+ce+" is pushed to collection")


# Get all cities from covid19India
with urlopen("https://api.covid19india.org/v2/state_district_wise.json") as cityurl:
    print("##### Got collection of all Cities")
    citiesData = json.loads(cityurl.read().decode())
    
with urlopen("https://api.covid19india.org/zones.json") as zoneurl:
    print("##### Got collection of all Zones")
    allZones = json.loads(zoneurl.read().decode())
    allZones = allZones['zones']
    
with urlopen("https://api.covid19india.org/resources/resources.json") as resourceURL:
    print("##### Got all resources for "+cs+"India"+ce)
    allResources = json.loads(resourceURL.read().decode())
    allResources = allResources['resources']
    
for stateList in citiesData:
    for city in stateList['districtData']:
        if city['district'] != 'Other State' or city['district'] != 'Unknown':
            resourceObj = {}
            cityData = {
                'city': city['district'],
                'notes': city['notes'],
                'active': city['active'],
                'confirmed': city['confirmed'],
                'deaths': city['deceased'],
                'recovered': city['recovered'],
                'delta': city['delta'],
                'statecode': stateList['statecode'],
                'state': stateList['state']
            }
            
            # add resources to cities
            for resource in allResources:
                if resource['city'] == city['district']:
                    resourceObj.setdefault(resource['category'].replace('.',''), []).append(resource)
                    # resourceObj.append(resource)
                pass
            pass
            if resourceObj:
                cityData['resources'] = resourceObj
                pass
            # check in zones for city data
            for zone in allZones:
                if zone['district'] == city['district']:
                    cityData['zone'] = zone['zone']
                    pass
                pass
            allCities.append(cityData)
            # cityCollection.insert_one(cityData)
            print("City: %s"%cityData['city'])
            pass
        pass
    pass

# Delete all documents from city test collection
delete = cityCollection.delete_many({})
print("##### Cleared all "+ cs + str(delete.deleted_count) + ce +" Documents deleted from "+ cs + str(cityCollection.name + ce))

# Insert allCities data to city test collection
cityCollection.insert_many(allCities)
print("##### Moved all "+ cs + str(len(allCities)) + ce +" documents to "+ cs + str(cityCollection.name) + ce)

# Delete all documents from city main collection
delete = mainCollection.delete_many({})
print("##### Cleared all "+ cs + str(delete.deleted_count) + ce+" documents from "+ cs + str(mainCollection.name) + ce)

# Insert allCities data to city main collection
mainCollection.insert_many(allCities)
print("##### Moved all "+ cs + str(len(allCities)) + ce +" documents to "+ cs + str(mainCollection.name) + ce)

print("##### "+cs+"Done bro"+ce+", check new collection")