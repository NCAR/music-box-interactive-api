from django.http import HttpResponse, HttpRequest
from .plot_setup import *
from django.shortcuts import render


# returns response with sub properties as buttons (species, rates, etc)
def get_contents(request):
    if request.method == 'GET':
        get = request.GET
        prop = get['type']

    response = HttpResponse()
    subs = sub_props(prop)
    for i in subs:
        response.write('<button class="sub_p" id=' + i + ">" + sub_props_names(i) + "</button>")
    return response


# returns plot in image buffer
def get(request):
    if request.method == 'GET':
        props = request.GET['type']
        buffer = output_plot(str(props))

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)



def custom(request):
    

    return HttpResponse()

