import sys
import os.path
from . import mpl_helper
import scipy.io
import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from matplotlib import pylab
from matplotlib.ticker import *
import matplotlib.pyplot as plt
from pylab import *
import PIL, PIL.Image, io
import pandas
from django.conf import settings

def sub_props(prop):
    mech_path = os.path.join(settings.BASE_DIR, "dashboard/static/mechanism/datamolec_info.json")
    with open(mech_path) as a:
            mechanism = json.loads(a.read())
    
    subs = []
    if prop == 'species':
        for molecule in mechanism['mechanism']['molecules']:
            subs.append(molecule['moleculename'])
    
    elif prop == 'rates':
        for photo in mechanism['mechanism']['photolysis']:
            subs.append(photo['tuv_reaction'])

        for reaction in mechanism['mechanism']['reactions']:
            reactants = reaction['reactants']
            products = []
            for i in reaction['products']:
                if int(i['coefficient']) > 1:
                    coef = str(i['coefficient'])
                else:
                    coef = ""
                molec = i['molecule']
                products.append(coef + molec)
            subs.append("+".join(i for i in reactants) + "->" + "+".join(j for j in reactants))
    return subs


def output_plot(prop):
    
    matplotlib.use('agg')

    (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
    

    # NetCDF output file
    nc_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.nc")
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    # if os.path.isfile(nc_results_path):
    #     ncf = scipy.io.netcdf_file(results_path)
    #     time = ncf.variables["time"].data.copy()
    #     for prop in props:
    #         var = ncf.variables[prop].data.copy()
    #         units = ncf.variables[prop].units
    #         axes.plot(time, var, "-", label=prop.replace("_", " "))
    # CSV output file
    if os.path.isfile(csv_results_path):
        csv = pandas.read_csv(csv_results_path)
        print(csv)
        csv_props = csv.columns
        units = "unknown"
        csv.plot(x="time", y=prop, ax=axes, legend=prop.replace("_", " "))
    else:
        return HttpResponseBadRequest('Missing results file', status=405)

    length = time[-1]
    grad = length / 6
    if grad < 700000:
        tick_spacing = [60, 3600, 7200, 14400, 18000, 21600, 25200, 36000, 43200, 86400, 172800, 345600, 604800]
        base = min(tick_spacing, key=lambda x: abs(x - grad))
        axes.xaxis.set_major_locator(plt.MultipleLocator(base))

    axes.set_xlabel(r"time / s")
    axes.set_ylabel(units.decode('utf-8'))
    axes.legend()
    axes.grid(True)

    # Store image in a string buffer
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png')

    plt.close(figure)

    return buffer



