from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from boxcar.models import Recipe
import logging
import json

logger = logging.getLogger(__name__)

## -- PAGES -- ##

def home(request):

    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def template(request):

    return render_to_response('template.html', {}, context_instance=RequestContext(request))

## -- AJAX -- ##

def get_cookbooks(request):

  search_term = request.POST.get('search_term', '')

  # Ok, I have a search term. Let's search...
  recipes = Recipe( **db.boxcar_cookbooks.find_one({'name': search_term}) )
  
  return HttpResponse(json.dumps(recipes), mimetype="application/json")

def create_environment(request):

    logger.info("POST: %s" %(request.POST))

    return HttpResponse(None, mimetype="application/json")