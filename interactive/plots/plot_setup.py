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
from .compare import *
from mechanism.species import tolerance_dictionary
from interactive.tools import *
from numpy import vectorize
import base64

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

model_output_units = 'mol/m-3'

def sub_props(prop, csv_results_path = os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv")):
    
    csv = pandas.read_csv(csv_results_path)
    titles = csv.columns.tolist()
    spec = list([])
    rate = list([])
    env = list([])
    for i in titles:
        if 'CONC' in i:
            if 'myrate__' not in i:
                spec.append(str(i).split('.')[1].rstrip())
            else:
                rate.append(str(i).split('myrate__')[1].rstrip())
        elif 'ENV' in i:
            env.append(str(i).split('.')[1].rstrip())
    if prop == 'species':
        logging.info('getting concentrations')
        return spec
    if prop == 'rates':
        logging.info('getting rates')
        return rate
    if prop == 'env':
        logging.info('getting conditions')
        return env
    if prop == 'compare':
        logging.info('getting runs')
        runs = get_valid_runs()
        return runs


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

def beautifyReaction(reaction):
    if '->' in reaction:
        reaction = reaction.replace('->', ' → ')
    if '_' in reaction:
        reaction = reaction.replace('_', ' + ')
    return reaction
def output_plot(prop, plot_units, csv_results_path=os.path.join(os.environ['MUSIC_BOX_BUILD_DIR'], "output.csv"), species_path=os.path.join(settings.BASE_DIR, "dashboard/static/config/camp_data/species.json")):
    matplotlib.use('agg')
        
    (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
    
    csv = pandas.read_csv(csv_results_path)
    titles = csv.columns.tolist()
    csv.columns = csv.columns.str.strip()
    subset = csv[['time', str(prop.strip())]]

    #make unit conversion if needed
    if plot_units:
        converter = vectorize(create_unit_converter(model_output_units, plot_units))
        if is_density_needed(model_output_units, plot_units):
            subset[str(prop.strip())] = converter(subset[str(prop.strip())], {'density': csv['ENV.number_density_air'].iloc[[-1]], 'density units':'mol/m-3 '})
        else:
            subset[str(prop.strip())] = converter(subset[str(prop.strip())])

    subset.plot(x="time", ax=axes)

    # time = subset[['time']].values.tolist()
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
        if 'myrate__' not in prop.split('.')[1]:
            axes.set_ylabel("("+plot_units+")")
            axes.set_title(beautifyReaction(name))
            #unit converter for tolerance      
            if plot_units:
                ppm_to_plot_units = create_unit_converter('ppm', plot_units)
            else:
                ppm_to_plot_units = create_unit_converter('ppm', model_output_units)
            print("* tolerance dictionary: ", tolerance_dictionary)
            if is_density_needed('ppm', plot_units):
                tolerance = ppm_to_plot_units(float(tolerance_dictionary(species_path)[name]), {'density': float(csv['ENV.number_density_air'].iloc[[-1]]), 'density units': 'mol/m-3 '})
            else:
                tolerance = ppm_to_plot_units(float(tolerance_dictionary(species_path)[name]))

            #this determines the minimum value of the y axis range. minimum value of ymax = tolerance * tolerance_yrange_factor
            tolerance_yrange_factor = 5
            ymax_minimum = tolerance_yrange_factor * tolerance
            property_maximum = subset[str(prop.strip())].max()
            if ymax_minimum > property_maximum:
                axes.set_ylim(-0.05 * ymax_minimum, ymax_minimum)
        else:
            name = name.split('__')[1]
            axes.set_ylabel(r"(mol/m^3 s^-1)")
            axes.set_title(beautifyReaction(name))
    elif prop.split('.')[0] == 'ENV':
        axes.set_title(sub_props_names(name))
        if name == 'temperature':
            axes.set_ylabel(r"K")
        elif name == 'pressure':
            axes.set_ylabel(r"Pa")
        elif name == 'number_density_air':
            axes.set_ylabel(r"moles/m^3")

    # axes.legend()
    axes.grid(True)
    axes.get_legend().remove()
    # Store image in a string buffer
    buffer = io.BytesIO()
    figure.savefig(buffer, format='png')

    plt.close(figure)
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded


# generates html for unit selection in plots sidebar
def plots_unit_select(prop):
    unit_choices = {
        'species': [
            'mol/m-3',
            'ppm',
            'ppb',
            'mol/mol',
            'mol/cm-3',
            'molecule/cm-3',
            'molecule/m-3'
        ]
    }
    response = ''
    if prop == 'species':
        choices = unit_choices[prop]
        response = '<div class="my-2"><div class="select-group"><label for="plotsUnitSelect">Select plot units</label><select class="form-control" id="plotsUnitSelect">'
        for choice in choices:
            response = response + '<option>' + choice + '</option>'
        response = response + '</select></div></div>'
        response = response + '<label>Select Species to Plot:</label>' # create label for species selection
    return response
