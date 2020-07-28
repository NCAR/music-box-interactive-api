from django.shortcuts import render
from .forms.speciesforms import *
from .csvload import handle_uploaded_csv
from .save import *


def new_species(request):

    if request.method == 'POST':
        new()

    context = {'form1': FormulaForm,
               'form2': InitForm,
               'form3': UnitForm(initial=unit_setup()),
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def species(request):

    if request.method == 'POST':
        newFormula = FormulaForm(request.POST)

        if newFormula.is_valid():
            with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json',
                      'w') as outfile:
                json.dump(newFormula.cleaned_data, outfile, indent=4)
            save("formula")
            formula_setup()

    context = {'form1': FormulaForm,
               'form2': InitForm,
               'form3': UnitForm(initial=unit_setup()),
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def values(request):

    if request.method == 'POST':
        newInits = InitForm(request.POST)

        if newInits.is_valid():
            with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json',
                      'w') as outfile:
                json.dump(newInits.cleaned_data, outfile, indent=4)
            save("value")
            value_setup()


    context = {'form1': FormulaForm,
               'form2': InitForm,
               'form3': UnitForm(initial=unit_setup()),
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def units(request):

    if request.method == 'POST':
        newUnits = UnitForm(request.POST)

        if newUnits.is_valid():
            with open('/Users/simonthomas/music-box-interactive/interactive/dashboard/static/config/post.json',
                      'w') as outfile:
                json.dump(newUnits.cleaned_data, outfile, indent=4)
            save("unit")
            unit_setup()

    context = {'form1': FormulaForm,
               'form2': InitForm,
               'form3': UnitForm(initial=unit_setup()),
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
    context = {}
    return render(request, 'config/options.html', context)


def options(request):
    context = {}
    return render(request, 'config/options.html', context)



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