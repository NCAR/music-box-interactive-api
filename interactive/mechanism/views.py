from django.shortcuts import render


def mechanism(request):
    context = {}
    return render(request, 'mechanism/reactions.html', context)


def molecules(request):
    context = {}
    return render(request, 'mechanism/molecules.html', context)


def reactions(request):
    context = {}
    return render(request, 'mechanism/reactions.html', context)
