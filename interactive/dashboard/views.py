from django.shortcuts import render
from .forms.speciesforms import *
from .forms.optionsforms import *
from .forms.initial_condforms import *
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
            load(newFormula.cleaned_data)
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
            load(newInits.cleaned_data)
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
            load(newUnits.cleaned_data)
            save("unit")
            unit_setup()

    context = {'form1': FormulaForm,
               'form2': InitForm,
               'form3': UnitForm(initial=unit_setup()),
               'csv_field': UploadFileForm
               }
    return render(request, 'config/species.html', context)


def csv(request):
    if request.method == 'POST':
        form = UploadFileForm( request.FILES)
        if form.is_valid():
            handle_uploaded_csv(request.FILES['file'])

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
    if request.method == 'POST':
        newOptions = OptionsForm(request.POST)

        if newOptions.is_valid():
            newOptions = newOptions.cleaned_data
            load(newOptions)
            save("options")
    option_setup()

    context = {
        'form': OptionsForm
    }
    return render(request, 'config/options.html', context)


def init(request):
    if request.method == 'POST':
        newConditions = InitialConditionsForm(request.POST)

        if newConditions.is_valid():
            newConditions = newConditions.cleaned_data
            load(newConditions)
            save("conditions")


    context = {
        'form': InitialConditionsForm,
        'unitform': ConditionsUnitsForm(initial=ini_cond_setup()['units']),
        'csv_field' : UploadInitFileForm
    }
    return render(request, 'config/init-cond.html', context)


def init_units(request):
    if request.method == 'POST':
        newUnits = ConditionsUnitsForm(request.POST)

        if newUnits.is_valid():
            newUnits = newUnits.cleaned_data
            load(newUnits)
            save("cond_units")


    context = {
        'form': InitialConditionsForm,
        'unitform': ConditionsUnitsForm(initial=ini_cond_setup()['units']),
        'csv_field' : UploadInitFileForm
    }
    return render(request, 'config/init-cond.html', context)


def init_csv(request):
    if request.method == 'POST':
        form = UploadFileForm( request.FILES)
        if form.is_valid():
            handle_uploaded_csv(request.FILES['file'])

    context = {
        'form': InitialConditionsForm,
        'unitform': ConditionsUnitsForm(initial=ini_cond_setup()['units']),
        'csv_field': UploadInitFileForm
    }
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

