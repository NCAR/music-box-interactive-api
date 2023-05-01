import pandas as pd
import numpy as np
from pyvis.network import Network


data = {'includedSpecies': ['M', 'Ar', 'CO2', 'H2O', 'O1D', 'O', 'O2', 'O3', 'N2'], 'blockedSpecies': [], 'startStep': 0, 'endStep': 1, 'maxArrowWidth': 7, 'arrowScalingType': 'log', 'minMolval': 0, 'maxMolval': 1, 'currentMinValOfGraph': 0, 'currentMaxValOfGraph': 1, 'isPhysicsEnabled': False, 'reactions': {'type': 'MECHANISM', 'name': 'music box interactive configuration', 'reactions': [{'type': 'PHOTOLYSIS', 'scaling_factor': 1, 'MUSICA name': 'O2_1', 'reactants': {'O2': {}}, 'products': {'O': {'yield': 2}, 'irr__0': {'yield': 1}}}, {'type': 'PHOTOLYSIS', 'scaling_factor': 1, 'MUSICA name': 'O3_1', 'reactants': {'O3': {}}, 'products': {'O1D': {'yield': 1}, 'O2': {'yield': 1}, 'irr__1': {'yield': 1}}}, {'type': 'PHOTOLYSIS', 'scaling_factor': 1, 'MUSICA name': 'O3_2', 'reactants': {'O3': {}}, 'products': {'O': {'yield': 1}, 'O2': {'yield': 1}, 'irr__2': {'yield': 1}}}, {'type': 'ARRHENIUS', 'A': 2.15e-11, 'Ea': -1.518e-21, 'B': 0, 'D': 300, 'E': 0, 'reactants': {'O1D': {'qty': 1}, 'N2': {'qty': 1}}, 'products': {'O': {'yield': 1}, 'N2': {'yield': 1}, 'irr__3': {'yield': 1}}}, {'type': 'ARRHENIUS', 'A': 3.3e-11, 'Ea': -7.59e-22, 'B': 0, 'D': 300, 'E': 0, 'reactants': {'O1D': {'qty': 1}, 'O2': {'qty': 1}}, 'products': {'O': {'yield': 1}, 'O2': {'yield': 1}, 'irr__4': {'yield': 1}}}, {'type': 'ARRHENIUS', 'A': 8e-12, 'Ea': 2.8428e-20, 'B': 0, 'D': 300, 'E': 0, 'reactants': {'O': {'qty': 1}, 'O3': {'qty': 1}}, 'products': {'O2': {'yield': 2}, 'irr__5': {'yield': 1}}}, {'type': 'ARRHENIUS', 'A': 6e-34, 'Ea': 0, 'B': -2.4, 'D': 300, 'E': 0, 'reactants': {'O': {'qty': 1}, 'O2': {'qty': 1}, 'M': {'qty': 1}}, 'products': {'O3': {'yield': 1}, 'M': {'yield': 1}, 'irr__6': {'yield': 1}}}]}}
reactions = data['reactions']['reactions']

df = pd.read_csv('/Users/kshores/Downloads/thing.csv')
rates = df[[x for x in df.columns if 'irr' in x]]

mapping = {}
species = set()

for reaction in reactions:
  for reactant in reaction['reactants']:
    species.add(reactant)
  irr = None
  for product in reaction['products']:
    if 'irr__' not in product:
      species.add(product)
    else:
      irr = product
  reactants = [f"{'' if v.get('qty') is None or v.get('qty') == 1 else v['qty']}{k}" for k, v in reaction["reactants"].items()]
  products = [f"{'' if v.get('yield') is None or v.get('yield') == 1 or k.startswith('irr') else str(v['yield'])}{k}" for k, v in reaction["products"].items() if not k.startswith('irr')]
  label = " + ".join(reactants) + " -> " + " + ".join(products)
  reaction['label'] = label
  reaction['irr'] = irr
  mapping[irr] = [x for x in df.columns if irr in x][0]

print(rates)
print(reactions)
print(mapping)

net = Network(directed=True)

# add the nodes for the reactions and species
for reaction in reactions:
    net.add_node(reaction['label'], label=reaction["label"])
for species in species:
    net.add_node(species)

# add the edges for the reactions and species
for reaction in reactions:
  print(reaction)
  for reactant in reaction["reactants"]:
    width = reaction["reactants"][reactant].get('qty', 1)
    net.add_edge(reactant, reaction['label'], width=width)
  for product in reaction["products"]:
    if 'irr__' not in product:
      intermediate_reaction_rate = df[mapping[reaction['irr']]].iloc[-1]
      width = reaction["products"][product].get('yield', 1) * intermediate_reaction_rate
      net.add_edge(reaction['label'], product, width=width)

# set the layout and show the graph
net.save_graph("reaction_graph.html")