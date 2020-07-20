from django.shortcuts import render


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
    context = {}
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