from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import logging
import json
from pymongo import MongoClient
from bson.json_util import dumps, default
import vagrantgen

logger = logging.getLogger(__name__)

# mongodb stuff
connection = MongoClient('localhost')
db = connection.boxcar_cookbooks

## -- PAGES -- ##

def home(request):

    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def generate(request):

    return render_to_response('generate.html', {}, context_instance=RequestContext(request))

## -- AJAX -- ##

def get_cookbooks(request):

    search_term = request.POST.get('search_term', '')

    # Ok, I have a search term. Let's search...
    # TODO: Make this a wildcard search that can return multiple results
    cursor = db.boxcar_cookbooks.find({'name': {'$regex':'^'+search_term}})

    cookbooks = []
    for c in cursor:
        cookbooks.append(c['name'])

    return HttpResponse(json.dumps(cookbooks))

def create_environment(request):

    print("POST: %s" %(request.POST))

    cookbooks = request.POST['cookbooks'].split(',')
    memory_size = request.POST['memory_size']
    memory_size_unit = request.POST['memory_size_unit']
    ports = request.POST['ports'].split(',')
    # TODO: Add box configuration to generate template, get value from POST
    box = 'precise64'

    print 'cookbooks: ',cookbooks
    print 'memory_size: ',memory_size
    print 'memory_size_unit: ',memory_size_unit
    print 'ports: ',ports
    print 'box: ',box

    logger.info('Gathering cookbooks...')
    recipes =[]
    for cookbook in cookbooks:
        recipes.append(Recipe( **db.boxcar_cookbooks.find_one({'name': cookbook}) ))

    logger.info('Generating environment...')
    vagrantgen.build_package(box='precise64', app_name='test_app', memory=512, recipes=recipes, port=3000)

    return HttpResponse("Create Environment", mimetype="application/json")
