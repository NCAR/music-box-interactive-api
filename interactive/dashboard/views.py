from django.shortcuts import render
from .forms.speciesforms import *
from .forms.optionsforms import *
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .forms.initial_reaction_rates_forms import *
from .upload_handler import *
from .save import *
from .models import Document
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
import os
from django.conf import settings
import mimetypes
from django.core.files import File
from interactive.tools import *
import pandas

def landing_page(request):
    context = {}
    return render(request, 'home.html', context)


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


def new_species(request):
    if request.method == 'POST':
        new()
    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return HttpResponseRedirect('/conditions/initial')


def species(request):
    if request.method == 'POST':
        new_spec = SpeciesForm(request.POST)
        if new_spec.is_valid():
            save_species(new_spec.cleaned_data)
    
    return HttpResponseRedirect('/conditions/initial')

def csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'conditions/species.html', context)

###########

def run_model(request):
    context = {}
    return render(request, 'run_model.html', context)

#renders plots page
def visualize(request):
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pandas.read_csv(csv_results_path)
    plot_property_list = [x.split('.')[0] for x in csv.columns.tolist()]
    plot_property_list = [x.replace(' ','') for x in plot_property_list]
    context = {
        'plots_list': plot_property_list
    }
    return render(request, 'plots.html', context)


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
    return render(request, 'conditions/options.html', context)

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
        'speciesform': SpeciesForm,
        'initial_reaction_rates_form': InitialReactionRatesForm,
        'csv_field' : UploadInitFileForm
    }
    return render(request, 'conditions/initial.html', context)


# add a new initial reaction rate or rate constant
def new_initial_reaction_rate(request):
    if request.method == 'GET':
        add_initial_reaction_rate()
    return HttpResponseRedirect('/conditions/initial#reaction-rates')


# save a set of initial reaction rates/rate constants
def initial_reaction_rates(request):
    if request.method == 'POST':
        new_rates = InitialReactionRatesForm(request.POST)
        if new_rates.is_valid():
            save_initial_reaction_rates(new_rates.cleaned_data)
    return HttpResponseRedirect('/conditions/initial#reaction-rates')

# remove a reaction from the list of initial reaction rates/rate constants
def remove_initial_reaction_rate(request):
    if request.method == 'GET':
        delete_initial_reaction_rate(request.GET['reaction'])
    return HttpResponseRedirect('/conditions/initial#reaction-rates')


# input file upload
def init_csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
    
    return HttpResponseRedirect('/conditions/initial')


#============== EVOLVING CONDITIONS PAGE ===============

def evolving_conditions(request):
    context = {
        'file_field': UploadEvolvFileForm(),
        'filedict': sorted(display_evolves().items())
        }
    return render(request, 'conditions/evolving.html', context)


def evolv_file(request):
    if request.method == 'POST':
        filename = str(request.FILES['file'])
        uploaded = request.FILES['file']
        manage_uploaded_evolving_conditions_files(uploaded, filename)
    return HttpResponseRedirect('/conditions/evolving')


def evolving_linear_combination(request):
    data = request.GET.dict()
    filename = data['filename'].replace('-', '.')
    data.pop('filename')
    combo = data.keys()
    save_linear_combo(filename, combo)

    return HttpResponseRedirect('/conditions/evolving')


def evolv_lr(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_loss_rates(uploaded)
    return HttpResponseRedirect('/conditions/evolving')


def clear_evolv_files(request):
    if request.method == 'GET':
        clear_e_files()
    return HttpResponseRedirect('/conditions/evolving')



def photo_ncf(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        print(str(request.FILES))
        handle_uploaded_p_rates(uploaded)
    return HttpResponseRedirect('/conditions/photolysis')


def photo_dt_form(request):
    if request.method == 'GET':
        response = HttpResponse()
        form = PhotoDatetimeForm()
        response.write('<form action="photo_start_results"><table>')
        for field in form:
            response.write('<tr><td>')
            response.write(field.name)
            response.write('</td><td>')
            response.write(field)
            response.write('</td></tr>')
        response.write('</table><button type="submit">Save</button></form>')
        return response
    else:
        return HttpResponse()


def save_photo_dt(request):
    if request.method == 'GET':
        dt = request.GET.dict()
        save_photo_start_time(dt)
    return HttpResponseRedirect('/conditions/photolysis')


def new_photo(request):
    if request.method == 'GET':
        new_photolysis()
    return HttpResponseRedirect('/conditions/photolysis')


def review(request):
    json = review_json()
    context = {
        "config": json
    }
    return render(request, 'conditions/review.html', context)


def remove(request):
    if request.method == 'GET':
        id = request.GET["species"]
        print(id)
        remove_species(id.split('.')[0])
    return HttpResponseRedirect('/configure/initial')


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
