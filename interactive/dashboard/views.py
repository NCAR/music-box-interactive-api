from django.shortcuts import render
from .forms.speciesforms import *
from .forms.optionsforms import *
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .forms.photolysisforms import *
from .upload_handler import *
from .save import *
from .models import Document
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
import os
from django.conf import settings
import mimetypes
from django.core.files import File
from interactive.tools import *


def landing_page(request):


    context = {}

    return render(request, 'landing.html', context)


######### species page


def csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
        

    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)

###########

def run_model(request):
    context = {}
    return render(request, 'run_model.html', context)


def visualize(request):
    context = {}
    return render(request, 'plots.html', context)



def configure(request):
    export()
    context = {
        'form': OptionsForm
    }
    return render(request, 'config/options.html', context)


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
    return render(request, 'config/options.html', context)


def config_json(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_json(uploaded)
        reverse_export()
    context = {
        'form': OptionsForm,
        'file_form': UploadJsonConfigForm
    }
    return render(request, 'config/options.html', context)

# ========== INITAL CONDITIONS PAGE =================

# initial conditions page render
def init(request):
    if request.method == 'POST':
        newConditions = InitialConditionsForm(request.POST)

        if newConditions.is_valid():
            newConditions = newConditions.cleaned_data
            save_init(newConditions)
            

    context = {
        'icform': InitialConditionsForm,
        'speciesform': SpeciesForm,
        'csv_field' : UploadInitFileForm
    }
    return render(request, 'config/init-cond.html', context)


# input file upload
def init_csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
        

    context = {
        'form': InitialConditionsForm,
        'csv_field': UploadInitFileForm
    }
    return HttpResponseRedirect('/configure/init-cond')

# species form
def species(request):

    if request.method == 'POST':
        new_spec = SpeciesForm(request.POST)
        if new_spec.is_valid():
            save_species(new_spec.cleaned_data)
 
    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return HttpResponseRedirect('/configure/init-cond')

#new species button
def new_species(request):
    if request.method == 'POST':
        new()

    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return HttpResponseRedirect('/configure/init-cond')

#remove species button
def remove(request):
    if request.method == 'GET':
        spec = request.GET["species"]
        spec = spec.split('.')[0]
        
        print(spec)
        remove_species(spec)

    return HttpResponse()


#============== EVOLVING CONDITIONS PAGE ===============


def evolv(request):
    context = {
        'csv_field': UploadEvolvFileForm(),
        'conditions': display_evolves(),
        'linear_combinations': display_linear_combinations(),
        'lr_field': UploadLossFileForm(),
        'is_lr_uploaded': check_loss_uploaded(),
    }
    return render(request, 'config/evolv-cond.html', context)


def evolv_csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_evolve(uploaded)
    return HttpResponseRedirect('/configure/evolv-cond')


def evolv_lr(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_loss_rates(uploaded)
    return HttpResponseRedirect('/configure/evolv-cond')


def clear_evolv_files(request):
    if request.method == 'GET':
        clear_e_files()
    return HttpResponseRedirect('/configure/evolv-cond')


def photolysis(request):
    if request.method == 'POST':
        newPhoto = PhotoForm(request.POST)

        if newPhoto.is_valid():
            newPhoto = newPhoto.cleaned_data
            save_photo(newPhoto)
            
    context = {
        'csv_field': UploadPhotoFileForm,
        'form': PhotoForm,
        'isUploaded': check_photo_uploaded(),
        'simstart': display_photo_start_time()
    }
    return render(request, 'config/photolysis.html', context)


def photo_ncf(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        print(str(request.FILES))
        handle_uploaded_p_rates(uploaded)
    
    return HttpResponseRedirect('/configure/photolysis')


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

    return HttpResponseRedirect('/configure/photolysis')


def new_photo(request):
    if request.method == 'GET':
        new_photolysis()
    
    return HttpResponseRedirect('/configure/photolysis')



def review(request):
    json = review_json()
    context = {
        "config": json
    }
    return render(request, 'config/review.html', context)


def download_file(request):
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/config/my_config.json')
    filename = 'my_config.json'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
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
    return HttpResponseRedirect('/configure/evolv-cond')


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
