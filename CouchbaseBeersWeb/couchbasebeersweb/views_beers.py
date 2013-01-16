from pyramid.view import view_config
from pyramid.response import Response
from couchbase.client import Couchbase
import json
import pyramid.httpexceptions as exc
from models import Beer

couchbase = Couchbase("127.0.0.1:8091", "beer-sample", "")
bucket = couchbase["beer-sample"]

@view_config(route_name="beers_index", renderer="templates/beers/index.jinja2")
def index(request):
    
    pageSize = 25 if request.params.get("pagesize") is None else int(request.params.get("pagesize"))
    startKey = "!" if request.params.get("startkey") is None else request.params.get("startkey")
    previousKey = "!" if request.params.get("previouskey") is None else request.params.get("previouskey")
    
    rows = bucket.view("_design/beers/_view/by_name", limit=pageSize+1, stale=False, startkey=json.dumps(startKey))
    def iter():
        for r in rows[0:pageSize-1]:
            try:
                json_str = bucket.get(r["id"].__str__())[2]
                beer = json.loads(json_str)
                beer["id"] = r["id"]
                yield beer
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
    
@view_config(route_name="beers_create", renderer="templates/beers/create.jinja2")
def create(request):
    return { }

@view_config(route_name="beers_create_post")
def create_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("beers_create"))
    
    beer = Beer()        
    for key in request.params:
        beer.__dict__[key] = request.params[key]
    
    bucket.set(beer.brewery_id + "-" + beer.name.replace(" ", "_"), 0, 0, json.dumps(beer.__dict__))
    raise exc.HTTPFound(request.route_url("beers_index"))
 
@view_config(route_name="beers_edit", renderer="templates/beers/edit.jinja2")
def edit(request):
    id = request.matchdict["id"]
    json_str = bucket.get(id)[2]
    beer_dict = json.loads(json_str)
    beer = Beer()    
    for key in beer_dict:
        beer.__dict__[key] = beer_dict[key]
    beer.id = id
    return { "model" : beer }
    
@view_config(route_name="beers_edit_post")
def edit_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("beers_edit"))
    
    beer = Beer() #would be safer to get the item first
    for key in request.params:
        beer.__dict__[key] = request.params[key]
    
    bucket.set(beer.name.replace(" ", "_"), 0, 0, json.dumps(beer.__dict__))
    raise exc.HTTPFound(request.route_url("beers_details", id=request.params["id"]))
        
@view_config(route_name="beers_delete", renderer="templates/beers/delete.jinja2")
def delete(request):
    id = request.matchdict["id"]
    json_str = bucket.get(id)[2]
    beer_dict = json.loads(json_str)
    beer = Beer()    
    for key in beer_dict:
        beer.__dict__[key] = beer_dict[key]
    beer.id = id
    return { "model" : beer }
    
@view_config(route_name="beers_delete_post")
def delete_post(request):
    if request.method != "POST":
        raise exc.HTTPFound(request.route_url("beers_delete"))
    
    bucket.delete(request.params["id"])
    raise exc.HTTPFound(request.route_url("beers_index"))
 
@view_config(route_name="beers_details", renderer="templates/beers/details.jinja2")
def details(request):
    id = request.matchdict["id"]
    json_str = bucket.get(id)[2]
    beer_dict = json.loads(json_str)
    beer = Beer()
    for key in beer_dict:
        beer.__dict__[key] = beer_dict[key]
    return { "model" : beer }