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
            response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="normal" id="' + i + '">☐ ' + beautifyReaction(sub_props_names(i)) + "</a>")
    elif prop == 'compare':
        for i in subs:
            response.write('<a href="#" class="sub_p list-group-item list-group-item-action" subType="compare" id="' + i + '">☐ ' + beautifyReaction(sub_props_names(i)) + "</a>")
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


#renders plots page
def visualize(request):
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pandas.read_csv(csv_results_path)
    plot_property_list = [x.split('.')[0] for x in csv.columns.tolist()]
    plot_property_list = [x.strip() for x in plot_property_list]
    for x in csv.columns.tolist():
        if "myrate" in x:
            plot_property_list.append('RATE')
    context = {
        'plots_list': plot_property_list
    }
    if os.path.isfile(csv_results_path):
        if os.path.getsize(csv_results_path) != 0:
            return render(request, 'plots.html', context)
        else:
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')
