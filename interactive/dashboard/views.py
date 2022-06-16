from django.shortcuts import render
from .forms.optionsforms import *
from .forms.report_bug_form import BugForm
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .flow_diagram import generate_flow_diagram, get_simulation_length, get_species
from .upload_handler import *
from .build_unit_converter import *
from .save import *
from .models import Document
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
import os
from django.conf import settings
import mimetypes
from django.core.files import File
from interactive.tools import *
import pandas
import platform
import codecs
import time
from io import TextIOWrapper


def landing_page(request):
    context = {
        'bugform': BugForm()
    }
    return render(request, 'home.html', context)


def report_bug(request):
    form_data = request.POST.dict()
    form_data.pop('csrfmiddlewaretoken')
        
    info = 'Operating system information: '+ str(os.name) + ' ' + str(platform.system()) + ' ' + str(platform.release())
    report = form_data['report']  
    report_dict = {'system info': info, 'report': report}

    create_report_zip(report_dict)
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/zip/output/config.zip')
    zip_file = open(fl_path, 'rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'bug_report.zip'
    return response


def example_file(request):
    filetype = request.GET.dict()['type']
    name = '/' + filetype + '.zip'
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/example_files/' + filetype + name)
    zip_file = open(fl_path, 'rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'example_' + filetype + '_file.zip'
    return response



def getting_started_page(request):
    context = {
        'configFileForm': UploadJsonConfigForm
    }
    return render(request, 'getting_started.html', context)


def load_example(request):
    example_name = 'example_' + str(request.GET.dict()['example'])
    load_example_configuration(example_name)
    return HttpResponseRedirect('/mechanism')


###########

def run_model(request):
    context = {}
    return render(request, 'run_model.html', context)

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

###############

###   Flow diagram page

#Base page render
def flow(request):

    context = {
        "species": get_species(),
        "simulation_length": get_simulation_length()
    }
    return render(request, 'flow.html', context)

#Flow diagram render
def get_flow(request):
    path_to_diagram = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/flow_plot.html")
    print("get_flow called")
    generate_flow_diagram(request.GET.dict())
    return HttpResponse()


def render_flow(request):
    
    time.sleep(0.1)
    path_to_diagram = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/flow_plot.html")
    return render(request, 'network_plot/flow_plot.html')

############

def conditions(request):
    export()
    context = {
        'form': OptionsForm
    }
    return render(request, 'conditions/options.html', context)


def options(request):
    if request.method == 'POST':
        newOptions = OptionsForm(request.POST)
        if newOptions.is_valid():
            newOptions = newOptions.cleaned_data
            load(newOptions)
            save("options")
    option_setup()
    context = {
        'form': OptionsForm,
        'file_form': UploadJsonConfigForm
    }
    return render(request, 'conditions/options.html', context)


def config_json(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_zip_config(uploaded)
        reverse_export()
    context = {
        'form': OptionsForm,
        'file_form': UploadJsonConfigForm
    }
    return HttpResponseRedirect('/mechanism/species')

# ========== INITAL CONDITIONS PAGE =================

# initial conditions page render
def initial_conditions(request):
    if request.method == 'POST':
        newConditions = InitialConditionsForm(request.POST)
        if newConditions.is_valid():
            newConditions = newConditions.cleaned_data
            save_init(newConditions)
    context = {
        'icform': InitialConditionsForm,
        'csv_field' : UploadInitFileForm,
        'unitTypes': getUnitTypes()
    }
    return render(request, 'conditions/initial.html', context)


# returns the list of initial conditions files
def initial_conditions_files_handler(request):
    values = initial_conditions_files()
    return JsonResponse(values)


# removes an initial conditions file
def initial_conditions_file_remove_handler(request):
    if request.method != "POST":
        return JsonResponse({"error":"removing initial conditions files should be a POST request"})
    remove_request = json.loads(request.body)
    initial_conditions_file_remove(remove_request)
    return JsonResponse({})


# returns the initial species concentrations
def initial_species_concentrations_handler(request):
    values = initial_species_concentrations()
    return JsonResponse(values)


# saves a set of initial species concentrations
def initial_species_concentrations_save_handler(request):
    if request.method != 'POST':
        return JsonResponse({"error":"saving initial concentrations should be a POST request"})
    initial_values = json.loads(request.body)
    initial_species_concentrations_save(initial_values)
    return JsonResponse({})


# returns the initial reaction rates/rate constants
def initial_reaction_rates_handler(request):
    values = initial_reaction_rates()
    return JsonResponse(values)


# saves a set of initial reaction rates
def initial_reaction_rates_save_handler(request):
    if request.method != 'POST':
        return JsonResponse({"error":"saving initial reaction rates should be a POST request"})
    initial_values = json.loads(request.body)
    initial_reaction_rates_save(initial_values)
    return JsonResponse({})


# input file upload
def init_csv(request):
    if request.method == 'POST':
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        manage_initial_conditions_files(uploaded, filename)
    return HttpResponseRedirect('/conditions/initial')


#============== EVOLVING CONDITIONS PAGE ===============

def evolving_conditions(request):
    context = {
        'file_field': UploadEvolvFileForm(),
        'filedict': sorted(display_evolves().items()),
        'linearcombinations': display_linear_combinations()
        }
    return render(request, 'conditions/evolving.html', context)


def evolv_file(request):
    if request.method == 'POST':
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        manage_uploaded_evolving_conditions_files(uploaded, filename)
    return HttpResponseRedirect('/conditions/evolving')


#removes linear combination from config
def remove_linear(request):
    if request.method == 'GET':
        filename = request.GET.dict()['name'].replace('-','.')
        config = open_json('my_config.json')
        evolving = config['evolving conditions']
        evolving.update({filename: {"linear combinations": {}}})
        config.update({'evolving conditions': evolving})
        dump_json('my_config.json', config)
    return HttpResponseRedirect('/conditions/evolving')


def evolving_linear_combination(request):
    data = request.GET.dict()
    filename = data['filename'].replace('-', '.')
    data.pop('filename')
    combo = data.keys()
    scale_factor = data.pop('scale_factor')
    save_linear_combo(filename, combo, scale_factor)

    return HttpResponseRedirect('/conditions/evolving')


def clear_evolv_files(request):
    if request.method == 'GET':
        clear_e_files()
    return HttpResponseRedirect('/conditions/evolving')


def download_file(request):
    create_config_zip()
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/zip/output/config.zip')
    zip_file = open(fl_path, 'rb')
    response = HttpResponse(zip_file, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'config.zip'
    return response


def linear_combination_form(request):
    form = LinearCombinationForm()
    response = HttpResponse()
    response.write('<form action="evolv-linear-combo" method="GET"><h3>')
    for field in form:
        response.write('<li>')
        response.write(field)
        response.write(field.name)
        response.write('</li>')
    response.write('<button type="submit">Add</button></h3></form>')
    return response


def evolv_linear_combo(request):
    if request.method == 'GET':
        comboDict = request.GET.dict()
        save_linear_combo(comboDict)
    return HttpResponseRedirect('/conditions/evolving')
    

def toggle_logging(request):
    if request.method == 'GET':
        resultDict = request.GET.dict()
        result = resultDict['isOn']
        lcfig = open_json('log_config.json')
        if "True" in result:
            lcfig.update({'logging_enabled': True})
        else:
            lcfig.update({'logging_enabled': False})
        dump_json('log_config.json', lcfig)
    return HttpResponse()


def toggle_logging_check(request):
    lcfig = open_json('log_config.json')
    isOn = lcfig['logging_enabled']
    return JsonResponse({"isOn": isOn})


def download_handler(request):
    context = {}
    return render(request, 'download.html', context)


def convert_values(request):
    unit_type = request.GET['type']
    new_unit = request.GET['new unit']
    initial_value = float(request.GET['value'])
    if any(c in unit_type for c in ('temperature', 'pressure')):
        response = convert_initial_conditions(unit_type, new_unit, initial_value)
    else:
        response = {}
    return JsonResponse(response)


def unit_options(request):
    unit_type = request.GET['unitType']
    response = make_unit_convert_form(unit_type)
    return response


# returns converted units
def convert_calculator(request):
    conversion_request = request.GET.dict()
    args = [x for x in conversion_request if 'args' in x]
    arg_dict = {}
    for key in conversion_request:
        if 'title' in key:
            arg_dict.update({conversion_request[key]: float(conversion_request[key.replace('title', 'value')])})
            arg_dict.update({conversion_request[key] + ' units': conversion_request[key.replace('title', 'unit')]})
    converter = create_unit_converter(conversion_request['initialUnit'], conversion_request['finalUnit'])
    if arg_dict:
        new_value = converter(float(conversion_request['initialValue']), arg_dict)
    else:
        new_value = converter(float(conversion_request['initialValue']))

    return HttpResponse(new_value)


# returns form fields for additional arguments in conversion
def unit_conversion_arguments(request):
    initial = request.GET['initialUnit']
    final = request.GET['finalUnit']
    arguments = get_required_arguments(initial, final)
    f = make_additional_argument_form(arguments)
    return f
