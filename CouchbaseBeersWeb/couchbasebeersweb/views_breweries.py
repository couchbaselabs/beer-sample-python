from pyramid.view import view_config
from pyramid.response import Response
from couchbase.client import Couchbase
import json
import pyramid.httpexceptions as exc
from models import Brewery, Beer

couchbase = Couchbase("127.0.0.1:8091", "beer-sample", "")
bucket = couchbase["beer-sample"]

@view_config(route_name="breweries_index", renderer="templates/breweries/index.jinja2")
def index(request):
    
    pageSize = 25 if request.params.get("pagesize") is None else int(request.params.get("pagesize"))
    startKey = "!" if request.params.get("startkey") is None else request.params.get("startkey")
    previousKey = "!" if request.params.get("previouskey") is None else request.params.get("previouskey")
    
    rows = bucket.view("_design/breweries/_view/by_name", limit=pageSize+1, stale=False, startkey=json.dumps(startKey))
    def iter():
        for r in rows[0:pageSize-1]:
            try:
                json_str = bucket.get(r["id"].__str__())[2]
                brewery = json.loads(json_str)
                brewery["id"] = r["id"]
                yield brewery
            except Exception, e:
                #yield { "name" : e }
                pass
        
    return {
            "model" : iter(), 
            "startKey" : rows[0]["key"], 
            "nextStartKey" : rows[len(rows)-1]["key"], 
            "previousKey" : previousKey, 
            "pageSize" : pageSize 
           }
    
@view_config(route_name="breweries_create", renderer="templates/breweries/create.jinja2")
def create(request):
    return { }

@view_config(route_name="breweries_create_post")
def create_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("breweries_create"))
    
    brewery = Brewery()        
    for key in request.params:
        brewery.__dict__[key] = request.params[key]
    
    bucket.set(brewery.name.replace(" ", "_"), 0, 0, json.dumps(brewery.__dict__))
    raise exc.HTTPFound(request.route_url("breweries_index"))
 
@view_config(route_name="breweries_edit", renderer="templates/breweries/edit.jinja2")
def edit(request):
    id = request.matchdict["id"]
    json_str = bucket.get(id)[2]
    brewery_dict = json.loads(json_str)
    brewery = Brewery()    
    for key in brewery_dict:
        brewery.__dict__[key] = brewery_dict[key]
    brewery.id = id
    return { "model" : brewery }
    
@view_config(route_name="breweries_edit_post")
def edit_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("breweries_edit"))
    
    brewery = Brewery() #would be safer to get the item first
    for key in request.params:
        brewery.__dict__[key] = request.params[key]
    
    bucket.set(request.params["id"], 0, 0, json.dumps(brewery.__dict__))
    raise exc.HTTPFound(request.route_url("breweries_details", id=request.params["id"]))
        
@view_config(route_name="breweries_delete", renderer="templates/breweries/delete.jinja2")
def delete(request):
    id = request.matchdict["id"]
    json_str = bucket.get(id)[2]
    brewery_dict = json.loads(json_str)
    brewery = Brewery()    
    for key in brewery_dict:
        brewery.__dict__[key] = brewery_dict[key]
    brewery.id = id
    return { "model" : brewery }
    
@view_config(route_name="breweries_delete_post")
def delete_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("breweries_delete"))
    
    bucket.delete(request.params["id"])
    raise exc.HTTPFound(request.route_url("breweries_index"))
 
@view_config(route_name="breweries_details", renderer="templates/breweries/details.jinja2")
def details(request):
    id = request.matchdict["id"]    
    rows = bucket.view("_design/breweries/_view/all_with_beers", stale=False, startkey=json.dumps([id, 0]), endkey=json.dumps([id, u"\uefff", 1]))
    
    json_str = bucket.get(id)[2]
    brewery_dict = json.loads(json_str)
    brewery = Brewery()
    for key in brewery_dict:
        brewery.__dict__[key] = brewery_dict[key]
        
    for row in rows[1:len(rows)]:
        try:
            json_str = bucket.get(row["id"])[2]
            beer_dict = json.loads(json_str)
            beer = Beer()    
            for key in beer_dict:
                beer.__dict__[key] = beer_dict[key]
            beer.id = id
            brewery.beers.append(beer)
        except Exception, e:
            pass
    
    return { "model" : brewery }