class Brewery(object):
    
    def __init__(self):
        self.id = ""
        self.name = ""
        self.city = ""
        self.state = ""
        self.code = ""
        self.country = ""
        self.website = ""
        self.description = ""
        self.addresses = []
        self.type = "brewery"
        self.beers = []
        
class Beer(object):

    def __init__(self):
        self.id = ""
        self.name = ""
        self.abv = 0.0
        self.ibu = 0.0
        self.srm = 0.0
        self.upc = 0.0
        self.brewery_id = ""
        self.description = ""
        self.style = ""
        self.category = ""
        self.type = "beer"