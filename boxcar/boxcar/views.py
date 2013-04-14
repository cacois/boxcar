from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import logging
import json
from pymongo import MongoClient
from bson.json_util import dumps, default
import vagrantgen
from boxcar.models import Recipe

logger = logging.getLogger(__name__)

## -- PAGES -- ##

def home(request):

    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def generate(request):

    return render_to_response('generate.html', {}, context_instance=RequestContext(request))

## -- AJAX -- ##

def get_cookbooks(request):

    search_term = request.POST.get('search_term', '')

    # Ok, I have a search term. Let's search...
    found_cookbooks = vagrantgen.cookbook_search(search_term)

    cookbooks = []
    for c in found_cookbooks:
        cookbooks.append(c['name'])

    return HttpResponse(json.dumps(cookbooks))

def create_environment(request):

    cookbooks = request.POST['cookbooks'].split(',')
    memory_size = request.POST['memory_size']
    memory_size_unit = request.POST['memory_size_unit']
    ports = request.POST['ports'].split(',')
    base_box = request.POST['base_box_name']
    app_name = 'app'

    print 'cookbooks: ',cookbooks
    print 'memory_size: ',memory_size
    print 'memory_size_unit: ',memory_size_unit
    print 'ports: ',ports
    print 'base_box: ',base_box

    logger.info('Gathering cookbooks...')
    recipes =[]
    for cookbook in cookbooks:
        recipes.append(Recipe( **vagrantgen.find_one_cookbook(cookbook) ))

    # build environment zip package
    logger.info('Generating environment...')
    zipfile_path = vagrantgen.build_package(base_box=base_box, app_name=app_name, memory=memory_size, recipes=recipes, ports=ports)

    # delete downloaded data
    vagrantgen.cleanup()

    return get_file_response(zipfile_path)

## -- HELPER METHODS -- ##

def get_file_response(filepath):
    import os.path
    import mimetypes

    try:
        fsock = open(filepath,"r")
        filename = os.path.basename(filepath)

        # take a guess at the mimetype of the specified file
        mimetype = mimetypes.guess_type(filename)
        
        if mimetype is not None:
            # create response
            response = HttpResponse(fsock, mimetype=mimetype[0])

        # add metadata to response
        response['Content-Disposition'] = 'attachment; filename=' + filename 

    except IOError:
        response = HttpResponseNotFound()

    return response
