import sys
import os.path
from . import mpl_helper
import scipy.io
import json
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib import pylab
from matplotlib.ticker import *
import matplotlib.pyplot as plt
from pylab import *
import PIL, PIL.Image, io
import pandas

def get(request):

    if request.method == 'GET':
        matplotlib.use('agg')

        (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
        props = request.GET.get('props', None).split(",")

        # NetCDF output file
        nc_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.nc")
        csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
        if os.path.isfile(nc_results_path):
            ncf = scipy.io.netcdf_file(results_path)
            time = ncf.variables["time"].data.copy()
            for prop in props:
                var   = ncf.variables[prop].data.copy()
                units = ncf.variables[prop].units
                axes.plot(time, var, "-", label=prop.replace("_"," "))
        # CSV output file
        elif os.path.isfile(csv_results_path):
            csv = pandas.read_csv(csv_results_path, index_col="time")
            csv_props = data.columns.str.strip('ENV.').strip('CONC.')
            data.columns = csv_props
            units = "unknown"
            time = csv.loc["time"]
            for prop in props:
                csv.plot(x="time", y=prop, ax=axes, legend=prop.replace("_"," "))
        else:
            return HttpResponseBadRequest('Missing results file', status=405)

        length = time[-1]
        grad = length / 6
        if grad < 700000:
            tick_spacing = [60, 3600, 7200, 14400, 18000, 21600, 25200, 36000, 43200, 86400, 172800, 345600, 604800]
            base = min(tick_spacing, key=lambda x:abs(x-grad))
            axes.xaxis.set_major_locator(plt.MultipleLocator(base))

        axes.set_xlabel(r"time / s")
        axes.set_ylabel(units.decode('utf-8'))
        axes.legend()
        axes.grid(True)


        # Store image in a string buffer
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png')

        plt.close(figure)

        # Send buffer in a http response the the browser with the mime type image/png set
        return HttpResponse(buffer.getvalue(), content_type="image/png")
    return HttpResponseBadRequest('Bad format for plot request', status=405)
