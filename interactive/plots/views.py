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
        response.write('<li><button class="sub_p" id=' + i + ">" + i + "</button></li>")
    return response


def get(request):

    if request.method == 'GET':
        props = request.GET['type']
        buffer = output_plot(props)

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)
