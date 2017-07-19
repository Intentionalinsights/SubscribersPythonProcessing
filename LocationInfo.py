class LocationInfo(object):

    def __init__(self, address, city, zipCode, country):
        self.address = address
        self.city = city
        self.zipCode = zipCode
        self.country = country


    def getFullAddress(self):
        return self.address + ", " + self.city + ", " + self.zipCode + ", " + self.country