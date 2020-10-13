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
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)



def sub_props(prop):
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pandas.read_csv(csv_results_path)
    titles = csv.columns.tolist()
   # print(titles, type(titles))
    spec = list([])
    rate = list([])
    env = list([])
    for i in titles:
        if 'CONC' in i:
            spec.append(str(i).split('.')[1])
        elif 'RATE' in i:
            rate.append(str(i).split('.')[1])
        elif 'ENV' in i:
            env.append(str(i).split('.')[1])
    if prop == 'species':
        logging.info('getting concentrations')
        return spec
    if prop == 'rates':
        logging.info('getting rates')
        return rate
    if prop == 'env':
        logging.info('getting conditions')
        return env


def undo_double(dataframe):
    dflist = dataframe.to_dict(orient='list')
    for key in dflist:
        for val in dflist[key]:
            i = dflist[key].index(val)
            old = val
            if 'D+' in old:
                delim = 'D+'
                multiple = 1
            elif 'D-' in old:
                delim = 'D-'
                multiple = -1
            exp = float(old.split(delim)[1]) * multiple
            number = float(old.split(delim)[0])
            new = number * (10 ** exp)
            dflist[key][i] = new
    return pandas.DataFrame(dflist)


def sub_props_names(subprop):
    namedict = {
        'temperature': "Temperature",
        'pressure': "Pressure",
        'number_density_air': "Density",
    }
    if subprop in namedict:
        return namedict[subprop]
    else:
        return subprop


def output_plot(prop):
    
    matplotlib.use('agg')

    (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
    csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")
    csv = pandas.read_csv(csv_results_path)
    subset = csv[['time', ' ' + str(prop)]]
    cleaned_subset = undo_double(subset)
    cleaned_subset.plot(x="time", ax=axes)

    # time = cleaned_subset[['time']].values.tolist()
    # length = time[-1][0]
    # grad = length / 6
    # if grad < 700000:
    #     tick_spacing = [60, 3600, 7200, 14400, 18000, 21600, 25200, 36000, 43200, 86400, 172800, 345600, 604800]
    #     base = min(tick_spacing, key=lambda x: abs(x - grad))
    #     axes.xaxis.set_major_locator(plt.MultipleLocator(base))

    # set labels and title
    axes.set_xlabel(r"time / s")
    name = prop.split('.')[1]
    if prop.split('.')[0] == 'CONC':
        axes.set_ylabel(r"(mol/m^3)")
        axes.set_title(name + ' Concentration vs. Time')
    elif prop.split('.')[0] == 'RATE':
        axes.set_ylabel(r"(mol/m^3 s^-1)")
        axes.set_title(name + ' Rate vs. Time')
    elif prop.split('.')[0] == 'ENV':
        axes.set_title(sub_props_names(name) + ' vs. Time')
        if name == 'temperature':
            axes.set_ylabel(r"K")
        elif name == 'pressure':
            axes.set_ylabel(r"Pa")
        
    axes.legend()
    axes.grid(True)
    
    # Store image in a string buffer
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png')

    plt.close(figure)

    return buffer


