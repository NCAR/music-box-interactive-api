from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .plot_setup import *
from django.shortcuts import render
from interactive.tools import *

# returns response with sub properties as buttons (species, rates, etc)
def get_contents(request):
    if request.method == 'GET':
        get = request.GET
        prop = get['type']

    response = HttpResponse()
    response.write(plots_unit_select(prop))
    subs = sub_props(prop)
    subs.sort()
    if prop != 'compare':
        for i in subs:
            response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="normal" id="' + i + '">☐ ' + sub_props_names(i) + "</a>")
    elif prop == 'compare':
        for i in subs:
            response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="compare" id="' + i + '">☐ ' + sub_props_names(i) + "</a>")
    return response


# returns plot in image buffer
def get(request):
    if request.method == 'GET':
        props = request.GET['type']
        if request.GET['unit'] == 'n/a':
            buffer = output_plot(str(props), False)
        else:
            buffer = output_plot(str(props), request.GET['unit'])

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)



def custom(request):
    

    return HttpResponse()


def compare(request):
    
    context = {
        'runs': get_valid_runs()
    }
    return render(request, 'pcompare.html', context)


def select_units(request):
    if request.method == 'GET':
        unit = request.GET['unit']
        dump_json('plots_configuration.json', {'unit': unit})

    return HttpResponse()
