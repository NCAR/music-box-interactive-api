from django.http import HttpResponse, HttpRequest
from .plot_setup import *
from django.shortcuts import render


def get_contents(request):
    if request.method == 'GET':
        get = request.GET
        prop = get['type']
        print(prop)

    response = HttpResponse()
    subs = sub_props(prop)
    for i in subs:
        response.write("<li><a>" + i + "</a></li>")
    return response


def get(request):

    if request.method == 'GET':
        buffer = output_plot(request)

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)
