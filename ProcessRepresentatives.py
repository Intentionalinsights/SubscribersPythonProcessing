import csv
import urllib2
import requests
import os
import json
import sys

from LocationInfo import LocationInfo
from PledgerLocation import PledgerLocation
from PledgerLocation import StateEncoder
from PledgerLocation import StateCodeMapping

#Global variables section to cleanup later***********
citizensDataLocation = 'data/take-the-pro-truth-pledge-all-subs-2017-08-07test.csv'
pledgeNumberIdToProcessFrom = 2582

processedFileNameForPledgersJsonData = "output/jsonPledgeResults.json"

shouldFetchAPIRepresentativeData = False
serverAPIRepresentativesUrl = 'https://content.googleapis.com/civicinfo/v2/representatives?address='
stateCodeToPledgersStateData = {} #dictionary will increment counts
countriesPledgersData = {}
countOfPTPEntriesNotValidForLookup = 0

with open(processedFileNameForPledgersJsonData) as data_file:
    jsonPledgeResultsPastData = data_file.read()
    if len(jsonPledgeResultsPastData) > 0:
        jsonDataPledgers = json.loads(jsonPledgeResultsPastData)
        for statePledgeData in jsonDataPledgers:
            stateName = statePledgeData['name']
            pledgerLocation = PledgerLocation(stateName, statePledgeData['code'], statePledgeData['publicOfficials'], statePledgeData["country"])
            pledgerLocation.setPreProccessedPledgersCount(statePledgeData['pledgersCount'])
            if len(pledgerLocation.code) > 0:
                stateCodeToPledgersStateData[stateName] = pledgerLocation
            else:
                countriesPledgersData[pledgerLocation.country] = pledgerLocation

stateCodeToNameMapper = StateCodeMapping()

def createLocationInfoFromRow(row):
    #TODO: extract validation rules out
    if str(row['Address 1']).__contains__('P.O'):
        return None
    if str(row['Address 1']).__contains__('PO Box'):
        return None
    if str(row['Address 1']).__contains__('/'):
        return None
    if str(row['Address 1']).__contains__(','):
        return None

    locationInfo = LocationInfo(row['Address 1'], row['City'], row['Region'], row['Zip'], row['Country'])
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

def addToCountryCount(locationInfo):
    if countriesPledgersData.has_key(locationInfo.country):
        countriesPledgersData[locationInfo.country].increasePledgeCount()
    else:
        print "New country found: " + locationInfo.country
        countriesPledgersData[locationInfo.country] = PledgerLocation("", "", "", locationInfo.country)

def countPledgersFromDataEntered(locationInfoList):
    for locationInfo in locationInfoList:
        print locationInfo.getFullAddress()

        if locationInfo.isUSBased() & locationInfo.hasValidStateData():
            if len(locationInfo.region) == 2:
                stateCode = locationInfo.region
                try:
                    stateName = stateCodeToNameMapper.stateCodeToFullNameDictionary[stateCode]
                    addToStateCount(stateName, stateCode, "", locationInfo.country)
                except:
                    e = sys.exc_info()[0]
                    print str(e) + " could not map stateCode " + stateCode + " to stateName."
            else:
                stateName = locationInfo.region
                try:
                    stateCode = stateCodeToNameMapper.stateNameToCodeDictionary[stateName]
                    addToStateCount(stateName, stateCode, "", locationInfo.country)
                except:
                    e = sys.exc_info()[0]
                    print str(e) + " could not map stateName " + stateName + " to stateCode."

        addToCountryCount(locationInfo)
        stateName = ""
        stateCode = ""


def addToStateCount(stateName, stateCode, representatives, country):
    if stateCodeToPledgersStateData.has_key(stateName):
        stateCodeToPledgersStateData[stateName].increasePledgeCount()
    else:
        print "New state found: " + stateName
        print "Adding new representatives to state: " + stateName
        print "Representatives: " + representatives
        stateCodeToPledgersStateData[stateName] = PledgerLocation(stateName, stateCode, representatives, country)

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

        addToStateCount(stateName, stateCode, representatives)

with open(citizensDataLocation, 'rb') as f:
    proTruthPledgersList = []  # each value in each column will be mapped to a list
    reader = csv.DictReader(f)
    for row in reader:
        if(int(row['#']) < pledgeNumberIdToProcessFrom):
            continue

        locationInfo = createLocationInfoFromRow(row)
        if locationInfo:
            proTruthPledgersList.append(locationInfo)
        else:
            countOfPTPEntriesNotValidForLookup += 1

    if (shouldFetchAPIRepresentativeData):
        findRepresentativesByAddressList(proTruthPledgersList, countOfPTPEntriesNotValidForLookup)
    else:
        countPledgersFromDataEntered(proTruthPledgersList)

pledgeSummaryData = stateCodeToPledgersStateData.values() + countriesPledgersData.values()

jsonPledgeResults = json.dumps(pledgeSummaryData, indent = 4, cls=StateEncoder)
print(jsonPledgeResults)
print('Number of invalid entries not valid for representative retrieval: ' + str(countOfPTPEntriesNotValidForLookup))

file = open(processedFileNameForPledgersJsonData, 'w')

file.write(jsonPledgeResults)

file.close()