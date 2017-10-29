class LocationInfo(object):

    def __init__(self, address, city, region, zipCode, country):
        self.address = address.strip()
        self.city = city.strip()
        if len(region) == 2:
            self.region = region.upper().strip()
        else:
            self.region = region.strip()
        self.zipCode = zipCode.strip()
        self.country = country.strip()

    def hasValidStateData(self):
        return len(self.region) >= 1

    def isUSBased(self):
        if self.country == 'United States':
            return True
        else:
            return False

    def getFullAddress(self):
        return "Address: " + self.address + " City: " + self.city + " Region:" + self.region + " ZipCode:" + self.zipCode + " Country:" + self.country