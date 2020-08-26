from django.http import HttpResponse, HttpRequest
from .plot_setup import output_plot
from django.shortcuts import render


def get_contents(request):
    if request.method == 'GET':
        get = request.GET
        print(get['type'])
    response = HttpResponse('<a>test</a>')
    return response


def get(request):

    if request.method == 'GET':
        buffer = output_plot(request)

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)
