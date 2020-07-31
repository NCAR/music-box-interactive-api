from django.shortcuts import render


def mechanism(request):
    context = {}
    return render(request, 'mechanism.html', context)
