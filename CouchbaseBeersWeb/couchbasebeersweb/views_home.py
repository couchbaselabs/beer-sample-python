from pyramid.view import view_config
from pyramid.response import Response

@view_config(route_name='home', renderer='templates/home/index.jinja2')
def home(request):
    return {'message':'Simple.  Fast.  Delicious.'}    