from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def home(request):

	return render_to_response('home.html', {}, context_instance=RequestContext(request))

def template(request):

	return render_to_response('template.html', {}, context_instance=RequestContext(request))

def get_cookbooks(request):

	return HttpResponse(None, mimetype="application/json")