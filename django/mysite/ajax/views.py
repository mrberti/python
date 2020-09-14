from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render
from django.urls import include, path
from django.views import generic

# Create your views here.
# class IndexView(generic.View):
#     template_name = "ajax/index.html"
    # print(include("ajax.urls"))
    # return HttpResponse("Test")
    # return render(request, "ajax/index.html")

def index(request):
    # template = loader.get_template("ajax/index.html")
    # print(template)
    # return HttpResponse(template.render())
    return render(request, "ajax/index.html")

def ajax(request):
    data = dict(request.GET)
    data["django"] = "GOTCHA!"
    return JsonResponse(data)

def sub(request):
    return HttpResponseRedirect()