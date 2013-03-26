from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

## -- PAGES -- ##

def home(request):

    return render_to_response('home.html', {}, context_instance=RequestContext(request))

def template(request):

    return render_to_response('template.html', {}, context_instance=RequestContext(request))

## -- AJAX -- ##

def get_cookbooks(request):

    search_term = request.POST.get('search_term', '')

    return HttpResponse(None, mimetype="application/json")

def create_environment(request):

    return HttpResponse(None, mimetype="application/json")