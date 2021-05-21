from pyvis.network import Network
import os
from django.conf import settings


def generate_network_plot():
    path_to_template = os.path.join(settings.BASE_DIR, "dashboard/templates/network_plot/plot.html")

    net = Network(directed=True)
    net.add_node(1)
    net.add_node(2)
    net.add_edge(1, 2)

    net.show(str(path_to_template))

