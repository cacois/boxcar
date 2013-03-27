from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import logging
import json
from pymongo import MongoClient
from bson.json_util import dumps

logger = logging.getLogger(__name__)

# mongodb stuff
connection = MongoClient('localhost')
db = connection.boxcar_cookbooks

## -- PAGES -- ##

def home(request):

    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def template(request):

    return render_to_response('template.html', {}, context_instance=RequestContext(request))

## -- AJAX -- ##

def get_cookbooks(request):

  search_term = request.POST.get('search_term', '')

  # Ok, I have a search term. Let's search...
  # TODO: Make this a wildcard search that can return multiple results
  recipes = db.boxcar_cookbooks.find({'name': {'$regex':'^'+search_term}})

  return HttpResponse(recipes, mimetype="application/json")

def create_environment(request):

    logger.info("POST: %s" %(request.POST))

    return HttpResponse(None, mimetype="application/json")
