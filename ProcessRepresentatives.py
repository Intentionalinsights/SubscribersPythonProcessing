import csv
import urllib2
import requests
import os
import json
import sys

from LocationInfo import LocationInfo

#Global variables section to cleanup later***********
#citizensDataLocation = 'data/take-the-pro-truth-pledge-all-subs-2017-06-28.csv'
citizensDataLocation = 'data/workingDataSet.csv'
serverAPIRepresentativesUrl = 'https://content.googleapis.com/civicinfo/v2/representatives?address='
stateToCitizenPTPSigningCount = {} #dictionary will increment counts
stateToRepresentativesMap = {} #dictionary will contain names of all officials tied to that state
countOfPTPEntriesNotValidForLookup = 0

def createLocationInfoFromRow(row):
    #TODO: extract validation rules out
    if not row['Address 1']:
        return None
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
        state = representativeInfoDetails['normalizedInput']['state']

        if stateToCitizenPTPSigningCount.has_key(state):
            stateToCitizenPTPSigningCount[state] = stateToCitizenPTPSigningCount[state] + 1
        else:
            print "New state found: " + state
            stateToCitizenPTPSigningCount[state] = 1

        if not representativeInfoDetails.get('officials'):
            countOfPTPEntriesNotValidForLookup += 1
            continue

        representatives = getRepresentativeNamesList(representativeInfoDetails['officials'])
        if not stateToRepresentativesMap.has_key(state):
            print "Adding new representatives to state: " + state
            print "Representatives: " + representatives
            stateToRepresentativesMap[state] = representatives

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


print(json.dumps(stateToCitizenPTPSigningCount, indent = 4))
print(json.dumps(stateToRepresentativesMap, indent = 4))
print('Number of invalid entries not valid for representative retrieval: ' + str(countOfPTPEntriesNotValidForLookup))