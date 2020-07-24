from django.shortcuts import render
from .forms import *

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
        newSpecies = SpeciesForm(request.POST)
        newInits = SpeciesForm(request.POST)
        newUnits = SpeciesForm(request.POST)


        if form1.is_valid():
            for key in form1.cleaned_data:
                print(form1.cleaned_data[key], key)
    return render(request, 'config/species.html', {'form1': SpeciesForm, 'form2': InitForm, 'form3': UnitForm})


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