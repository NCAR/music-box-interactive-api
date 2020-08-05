from django.http import HttpResponse
from .plot_setup import output_plot


def get(request):

    if request.method == 'GET':
        buffer = output_plot()

        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)
