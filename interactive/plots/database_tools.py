from dashboard import models
from io import StringIO, BytesIO
from numpy import vectorize
from plots import mpl_helper
from pyvis.network import Network
from shared.utils import beautifyReaction, is_density_needed, create_unit_converter, sub_props_names

import dashboard.database_tools as db_tools
import logging
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s',
                    level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s - [ERROR!!] %(message)s',
                    level=logging.ERROR)

# generate network plot for user
def generate_database_network_plot(uid, species, path_to_template):
    user = db_tools.get_user(uid)
    reactions_data = user.config_files['/camp_data/reactions.json']
    net = Network(directed=True)
    contained_reactions = {}

    for r in reactions_data['camp-data'][0]['reactions']:
        if 'reactants' in r:
            tmp = reactions_data['camp-data'][0]['reactions']
            if species in r['reactants']:
                contained_reactions.update({tmp.index(r): {}})
            if species in r['products']:
                contained_reactions.update({tmp.index(r): {}})

    logging.debug(contained_reactions)
    nodes = {}
    edges = []

    if contained_reactions:
        for i in contained_reactions:
            tmp = reactions_data['camp-data'][0]['reactions']
            reac_data = tmp[i]['reactants']
            prod_data = tmp[i]['products']
            reactants = [x for x in reac_data]
            products = [x for x in prod_data]
            first = '+'.join(reactants)
            second = '+'.join(products)
            name = first + '->' + second
            net.add_node(name, label=name,  color='green',
                         borderWidthSelected=3)
            for j in reactants:
                nodes.update({j: {}})
                edges.append([j, name])
            for k in products:
                nodes.update({k: {}})
                edges.append([name, k])
    else:
        net.add_node(species, label=species, )
    if species in nodes:
        nodes.pop(species)
    net.add_node(species, label=species, color='blue', size=50)
    for n in nodes:
        net.add_node(n, label=n, borderWidthSelected=3, size=40)
    for e in edges:
        net.add_edge(e[0], e[1])
    # manually create temp file for pyvis to use
    # on this production server, pyvis doesn't have perms. to create it
    # if not os.path.exists('./'+str(path_to_template)):
        # tmp = open(str(path_to_template), 'w')
        # logging.info('manually created template file ./'+str(path_to_template))
    net.force_atlas_2based(gravity=-100, overlap=1)
    # generate the plot, return html code and delete the file
    net.write_html(uid + '_network.html')
    with open(uid + '_network.html', 'r') as f:
        html = f.read()
    os.remove(uid + '_network.html')
    return html


# get plot from model run
def get_plot(uid, prop, plot_units):
    # get output.csv from model run
    model = models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results['/output.csv'])
    matplotlib.use('agg')
        
    (figure, axes) = mpl_helper.make_fig(top_margin=0.6, right_margin=0.8)
    csv = pd.read_csv(output_csv, encoding='latin1')
    titles = csv.columns.tolist()
    csv.columns = csv.columns.str.strip()
    subset = csv[['time', str(prop.strip())]]
    model_output_units = 'mol/m-3'
    #make unit conversion if needed
    if plot_units:
        converter = vectorize(create_unit_converter(model_output_units, plot_units))
        if is_density_needed(model_output_units, plot_units):
            subset[str(prop.strip())] = converter(subset[str(prop.strip())], {'density': csv['ENV.number_density_air'].iloc[[-1]], 'density units':'mol/m-3 '})
        else:
            subset[str(prop.strip())] = converter(subset[str(prop.strip())])

    subset.plot(x="time", ax=axes)

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

            if is_density_needed('ppm', plot_units):
                density = float(csv['ENV.number_density_air'].iloc[[-1]])
                pp = float(db_tools.tolerance(uid)[name])
                du = 'density units'
                units = 'mol/m-3 '
                de = 'density'
                tolerance_tmp = ppm_to_plot_units(pp, {de: density, du: units})
            else:
                pp = float(db_tools.tolerance(uid)[name])
                tolerance_tmp = ppm_to_plot_units(pp)

            #this determines the minimum value of the y axis range. minimum value of ymax = tolerance * tolerance_yrange_factor
            tolerance_yrange_factor = 5
            ymax_minimum = tolerance_yrange_factor * tolerance_tmp
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
    buffer = BytesIO()
    figure.savefig(buffer, format='png')
    plt.close(figure)
    return buffer