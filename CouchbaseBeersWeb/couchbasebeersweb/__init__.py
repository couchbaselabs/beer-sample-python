from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view("static", "static", cache_max_age=3600)
    config.include("pyramid_jinja2")
    config.add_jinja2_search_path("/templates")
    config.add_route("home", "/")       
    
    #beers
    config.add_route("beers_index", "/beers/index")
    config.add_route("beers_create", "/beers/create")
    config.add_route("beers_create_post", "/beers/save/create")    
    config.add_route("beers_edit", "/beers/edit/{id}")   
    config.add_route("beers_edit_post", "/beers/save/edit")
    config.add_route("beers_delete", "/beers/delete/{id}")
    config.add_route("beers_delete_post", "/beers/save/delete")
    config.add_route("beers_details", "/beers/details/{id}")
    
    #breweries
    config.add_route("breweries_index", "/breweries/index")
    config.add_route("breweries_create", "/breweries/create")
    config.add_route("breweries_create_post", "/breweries/save/create")    
    config.add_route("breweries_edit", "/breweries/edit/{id}")   
    config.add_route("breweries_edit_post", "/breweries/save/edit")
    config.add_route("breweries_delete", "/breweries/delete/{id}")
    config.add_route("breweries_delete_post", "/breweries/save/delete")
    config.add_route("breweries_details", "/breweries/details/{id}")
    config.scan()
    
    #countries
    config.add_route("countries_index", "/countries/index")
    config.add_route("countries_provinces", "/countries/provinces/{country}")
    config.add_route("countries_cities", "/countries/cities/{country}/{province}")
    config.add_route("countries_codes", "/countries/codes/{country}/{province}/{city}")
    config.add_route("countries_details", "/countries/details/{country}/{province}/{city}/{code}")
        
    return config.make_wsgi_app()
