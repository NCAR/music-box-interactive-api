from django.shortcuts import render
from .forms.speciesforms import *
from .forms.optionsforms import *
from .forms.evolvingforms import *
from .forms.initial_condforms import *
from .forms.photolysisforms import *
from .upload_handler import *
from .save import *
from .models import Document
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
import os
from django.conf import settings
import mimetypes
from django.core.files import File

def new_species(request):
    if request.method == 'POST':
        new()

    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def species(request):

    if request.method == 'POST':
        new_spec = SpeciesForm(request.POST)
        if new_spec.is_valid():
            save_species(new_spec.cleaned_data)

    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
        

    context = {'form1': SpeciesForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


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


def init(request):
    if request.method == 'POST':
        newConditions = InitialConditionsForm(request.POST)

        if newConditions.is_valid():
            newConditions = newConditions.cleaned_data
            save_init(newConditions)
            

    context = {
        'form': InitialConditionsForm,
        'csv_field' : UploadInitFileForm
    }
    return render(request, 'config/init-cond.html', context)


def init_csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        uploaded_to_config(handle_uploaded_csv(uploaded))
        

    context = {
        'form': InitialConditionsForm,
        'csv_field': UploadInitFileForm
    }
    return render(request, 'config/init-cond.html', context)


def evolv(request):
    context = {
        'csv_field': UploadEvolvFileForm,
        'conditions': display_evolves()

    }
    return render(request, 'config/evolv-cond.html', context)


def evolv_csv(request):
    if request.method == 'POST':
        uploaded = request.FILES['file']
        handle_uploaded_evolve(uploaded)
    return HttpResponseRedirect('/configure/evolv-cond')


def photolysis(request):
    if request.method == 'POST':
        newPhoto = PhotoForm(request.POST)

        if newPhoto.is_valid():
            newPhoto = newPhoto.cleaned_data
            save_photo(newPhoto)
            
    context = {
        'csv_field': UploadPhotoFileForm,
        'form': PhotoForm
    }
    return render(request, 'config/photolysis.html', context)


def photo_csv(request):

    context = {
        'csv_field': UploadPhotoFileForm,
        "form": PhotoForm
    }
    return render(request, 'config/photolysis.html', context)


def new_photo(request):
    if request.method == 'GET':
        new_photolysis()
    
    return HttpResponse()


def review(request):
    json = review_json()
    context = {
        "config": json
    }
    return render(request, 'config/review.html', context)


def remove(request):
    if request.method == 'GET':
        id = request.GET["species"]
        print(id)
        remove_species(id)

    return HttpResponse()


def download_file(request):
    fl_path = os.path.join(settings.BASE_DIR, 'dashboard/static/config/my_config.json')
    filename = 'my_config.json'

    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
