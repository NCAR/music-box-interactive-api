from django.shortcuts import render

def run_model(request):
    context = {}
    return render(request, 'run_model.html', context)

def visualize(request):
    context = {}
    return render(request, 'plots.html', context)

def configure(request):
    context = {}
    return render(request, 'configure.html', context)

