from pyramid.view import view_config
from pyramid.response import Response
from couchbase.client import Couchbase
import json
import pyramid.httpexceptions as exc
from models import Brewery, Beer

couchbase = Couchbase("127.0.0.1:8091", "beer-sample", "")
bucket = couchbase["beer-sample"]

@view_config(route_name="countries_index", renderer="templates/countries/index.jinja2")
def index(request):
        
    rows = bucket.view("_design/breweries/_view/by_country", stale=False, group=True, group_level=1)
    def iter():
        for r in rows:
            try:                
                yield (r["key"][0], r["value"])
            except Exception, e:
                yield { "name" : e }
        
    return { "model" : iter() }
    
@view_config(route_name="countries_provinces", renderer="templates/countries/provinces.jinja2")
def provinces(request):
    
    startkey = [request.matchdict["country"]]
    endkey = [i for i in startkey]
    endkey.append(u"\uefff")
    
    rows = bucket.view("_design/breweries/_view/by_country", stale=False, group=True, group_level=2, startkey=json.dumps(startkey), endkey=json.dumps(endkey))
    def iter():
        for r in rows:
            try:                
                yield (r["key"][0], r["key"][1], r["value"])
            except Exception, e:
                yield { "name" : e }
        
    return { "model" : iter(), "country" : request.matchdict["country"] }

@view_config(route_name="countries_cities", renderer="templates/countries/cities.jinja2")
def cities(request):
    
    startkey = [request.matchdict["country"], request.matchdict["province"]]
    endkey = [i for i in startkey]
    endkey.append(u"\uefff")
    
    rows = bucket.view("_design/breweries/_view/by_country", stale=False, group=True, group_level=3, startkey=json.dumps(startkey), endkey=json.dumps(endkey))
    def iter():
        for r in rows:
            try:                
                yield (r["key"][0], r["key"][1], r["key"][2], r["value"])
            except Exception, e:
                yield { "name" : e }
        
    return { "model" : iter(), "country" : request.matchdict["country"], "province" : request.matchdict["province"] }      

@view_config(route_name="countries_codes", renderer="templates/countries/codes.jinja2")
def codes(request):
    
    startkey = [request.matchdict["country"], request.matchdict["province"], request.matchdict["city"]]
    endkey = [i for i in startkey]
    endkey.append(u"\uefff")
    
    rows = bucket.view("_design/breweries/_view/by_country", stale=False, group=True, group_level=4, startkey=json.dumps(startkey), endkey=json.dumps(endkey))
    def iter():
        for r in rows:
            try:                
                yield (r["key"][0], r["key"][1], r["key"][2], r["key"][3], r["value"])
            except Exception, e:
                yield { "name" : e }
        
    return { "model" : iter(), "country" : request.matchdict["country"], "province" : request.matchdict["province"], "city" : request.matchdict["city"] }       
    
@view_config(route_name="countries_details", renderer="templates/countries/details.jinja2")
def details(request):
    
    key = [request.matchdict["country"], request.matchdict["province"], request.matchdict["city"], request.matchdict["code"]]
    
    rows = bucket.view("_design/breweries/_view/by_country", stale=False, reduce=False, key=key)
    def iter():
        for r in rows:
            try:
                brewery = Brewery()
                brewery_json = bucket.get(r["id"])[2]
                brewery_dict = json.loads(brewery_json)
                for key in brewery_dict:
                    brewery.__dict__[key] = brewery_dict[key]
                brewery.id = r["id"]
                yield brewery
            except Exception, e:
                yield { "name" : e }
        
    return \
        { 
            "model" : iter(),
            "key" : key
        }