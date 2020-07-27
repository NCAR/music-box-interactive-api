from django.shortcuts import render
from .forms.speciesforms import *
from .csvload import handle_uploaded_csv

def run_model(request):
    context = {}
    return render(request, 'run_model.html', context)


def visualize(request):
    context = {}
    return render(request, 'plots.html', context)


def configure(request):
    context = {}
    return render(request, 'config/options.html', context)


def options(request):
    context = {}
    return render(request, 'config/options.html', context)


def species(request):
    if request.method == 'POST':
        csv = UploadFileForm(request.POST, request.FILES)
        newSpecies = SpeciesForm(request.POST)
        newInits = InitForm(request.POST)
        newUnits = UnitForm(request.POST)

        if csv.is_valid():
            handle_uploaded_csv(request.FILES['file'])

            # Dictionaries arent ordered. must find a way to order values into list correctly

        if newSpecies.is_valid():
            print(newSpecies.cleaned_data)

        if newInits.is_valid():
            print(newInits.cleaned_data)

        if newUnits.is_valid():
            print(newUnits.cleaned_data)




    context = {'form1': SpeciesForm,
               'form2': InitForm,
               'form3': UnitForm,
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def init(request):
    context = {}
    return render(request, 'config/init-cond.html', context)


def evolv(request):
    context = {}
    return render(request, 'config/evolv-cond.html', context)


def photolysis(request):
    context = {}
    return render(request, 'config/photolysis.html', context)


def review(request):
    context = {}
    return render(request, 'config/review.html', context)