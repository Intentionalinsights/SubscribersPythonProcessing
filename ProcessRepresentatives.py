import csv
import urllib2
import requests
import os
import json
import sys

from LocationInfo import LocationInfo
from StateData import StateData
from StateData import StateEncoder
from StateData import StateCodeMapping

#Global variables section to cleanup later***********
#citizensDataLocation = 'data/take-the-pro-truth-pledge-all-subs-2017-06-28.csv'
citizensDataLocation = 'data/workingDataSet.csv'
serverAPIRepresentativesUrl = 'https://content.googleapis.com/civicinfo/v2/representatives?address='
stateCodeToPledgersStateData = {} #dictionary will increment counts
countOfPTPEntriesNotValidForLookup = 0

stateCodeToNameMapper = StateCodeMapping()

def createLocationInfoFromRow(row):
    #TODO: extract validation rules out
    #API can still return results if a city, or zip is entered
    #enable this rule if we only want to allow counting results via address provided.
    #if not row['Address 1']:
    #    return None
    if not row['Country']  == 'United States':
        return None
    if str(row['Address 1']).__contains__('P.O'):
        return None
    if str(row['Address 1']).__contains__('PO Box'):
        return None
    if str(row['Address 1']).__contains__('/'):
        return None
    if str(row['Address 1']).__contains__(','):
        return None

    #print "Adding address: " + row['Address 1']
    locationInfo = LocationInfo(row['Address 1'], row['City'], row['Zip'], row['Country'])
    return locationInfo

def getRequestUrlForAddress(addressQueryInfo):
    return serverAPIRepresentativesUrl + requests.utils.quote(addressQueryInfo) \
           + "&levels=administrativeArea1" \
           + "&alt=json&key=" + os.environ['GOOGLE_KEY']

def getRepresentativeNamesList(officialsList):
    officialsNames = []
    for official in officialsList:
        officialsNames.append(official['name'])
    return ','.join(officialsNames)

def fetchDataForCivicAddress(encodedUrl):
    try:
        return urllib2.urlopen(encodedUrl).read()
    except:
        e = sys.exc_info()[0]
        print e
        return None

def findRepresentativesByAddressList(locationInfoList, countOfPTPEntriesNotValidForLookup):
    for entry in locationInfoList:
        print entry.getFullAddress()
        encodedUrl = getRequestUrlForAddress(entry.getFullAddress())
        print encodedUrl

        civicAPIResponse = fetchDataForCivicAddress(encodedUrl)
        if not civicAPIResponse:
            countOfPTPEntriesNotValidForLookup += 1
            continue

        representativeInfoDetails = json.loads(civicAPIResponse)
        if not representativeInfoDetails.get('officials'):
            countOfPTPEntriesNotValidForLookup += 1
            continue

        stateCode = representativeInfoDetails['normalizedInput']['state']
        stateName = stateCodeToNameMapper.stateCodeToFullNameDictionary[stateCode]
        representatives = getRepresentativeNamesList(representativeInfoDetails['officials'])

        if stateCodeToPledgersStateData.has_key(stateName):
            stateCodeToPledgersStateData[stateName].increasePledgeCount()
        else:
            print "New state found: " + stateName
            print "Adding new representatives to state: " + stateName
            print "Representatives: " + representatives
            stateCodeToPledgersStateData[stateName] = StateData(stateName, stateCode, representatives)

with open(citizensDataLocation, 'rb') as f:
    proTruthPledgersList = []  # each value in each column will be mapped to a list
    reader = csv.DictReader(f)
    for row in reader:
        locationInfo = createLocationInfoFromRow(row)
        if locationInfo:
            proTruthPledgersList.append(locationInfo)
        else:
            countOfPTPEntriesNotValidForLookup += 1

    findRepresentativesByAddressList(proTruthPledgersList, countOfPTPEntriesNotValidForLookup)

pledgeSummaryData = stateCodeToPledgersStateData.values()

jsonPledgeResults = json.dumps(pledgeSummaryData, indent = 4, cls=StateEncoder)
print(jsonPledgeResults)
print('Number of invalid entries not valid for representative retrieval: ' + str(countOfPTPEntriesNotValidForLookup))

file = open("output/jsonPledgeResults.json", "w")

file.write(jsonPledgeResults)

file.close()