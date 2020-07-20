from django.shortcuts import render

# Create your views here.

def some_view(request):


    return render(request, 'form.html', {'form': CustomForm()})

