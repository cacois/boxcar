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
  recipes = db.boxcar_cookbooks.find_one({'name': search_term})
  
  return HttpResponse(dumps(recipes), mimetype="application/json")

def create_environment(request):

  return HttpResponse(None, mimetype="application/json")