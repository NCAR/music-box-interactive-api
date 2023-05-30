from io import StringIO
from pyvis.network import Network
import api.models
import numpy as np
import pandas as pd
import logging
import os
import json

logger = logging.getLogger(__name__)


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


# time interval should be in format [small, large]
# and have a minimum difference greater than or equal to the model timestep
def return_valid_df_time_indices(df, user_time_range, model_timestep):
    logger.info(f"user_time_range {user_time_range}")
    logger.info(f"model_timestep {model_timestep}")
    full_time_range = np.array(
        [df["time"].index[0], df["time"].index[-1]], dtype=np.int64
    )
    if user_time_range[1] < user_time_range[0]:
        return full_time_range
    if user_time_range[1] - user_time_range[0] <= (model_timestep / 2):
        return full_time_range
    return np.array(
        [
            (df["time"] - user_time_range[0]).abs().argsort()[:1][0],
            (df["time"] - user_time_range[1]).abs().argsort()[:1][0],
        ],
        dtype=np.int64,
    )


# Simple logic check on user inputed time range
# to ensure that it is in format [small, large]
def return_valid_df_filter_range(user_filter_range):
    if user_filter_range[0] < user_filter_range[1]:
        return user_filter_range
    else:
        return [0, 1000000]


# get flux returns the sum of the differences between each timestep
# divided by the length of the array
# divided by the size of the timestep.
# Resultant units should be (change in concentration)/time
def get_flux(series, model_time_range_indices, model_timestep):
    series_sum = sum(
        np.diff(
            series[
                model_time_range_indices[0] : model_time_range_indices[1] + 1
            ]
        )
    )

    series_length = len(
        series[model_time_range_indices[0] : model_time_range_indices[1] + 1]
    )
    return series_sum / series_length / model_timestep


# getting flux before graphing.
# TODO: This step is inefficient and could possibly be eliminated by using
# the mapping dict in a single loop
def get_flux_min_max(df, model_time_range_indices, model_timestep):
    flux_list = []
    for name, values in df.items():
        if "irr" in name:
            flux_list.append(
                get_flux(
                    series=values,
                    model_timestep=model_timestep,
                    model_time_range_indices=model_time_range_indices,
                )
            )
    return [min(flux_list), max(flux_list)]


# scales arrows using the user selected max arrow width,
# with a minimum width of 1.
# This may benefit from a different scaling curve or log base
def scale_arrow_width(
    width, raw_flux_min_max, display_min_max, user_arrow_scaling_type
):
    if user_arrow_scaling_type == "linear":
        return np.interp(width, raw_flux_min_max, display_min_max)
    if user_arrow_scaling_type == "log":
        return np.interp(
            np.log(width), np.log(raw_flux_min_max), display_min_max
        )


# main function
def generate_flow_diagram(request_dict, uid):
    ########################
    # get data to build with
    ########################
    model = api.models.ModelRun.objects.get(uid=uid)
    output_csv = StringIO(model.results["/output.csv"])
    df = pd.read_csv(output_csv, encoding="latin1")  # result of modeling
    model_timestep = int(df["time"].iloc[1] - df["time"].iloc[0])

    ###########################
    # get user selectable input
    ###########################
    user_width_scaling = float(request_dict["maxArrowWidth"])
    user_arrow_scaling_type = request_dict["arrowScalingType"]
    user_time_range = [request_dict["startStep"], request_dict["endStep"]]
    user_filter_range = [
        float(request_dict["minMolval"]),
        float(request_dict["maxMolval"]),
    ]
    user_filter_toggle = request_dict["showFilteredNodesAndEdges"]
    user_blocked_species = request_dict["blockedSpecies"]
    user_disabled_physics = request_dict["isPhysicsEnabled"]

    reactions = request_dict["reactions"]["reactions"]

    #######################################################
    # process user selections to use with modeling results:
    #######################################################
    model_time_range_indices = return_valid_df_time_indices(
        df=df, user_time_range=user_time_range, model_timestep=model_timestep
    )
    # for use with display_width calculation.
    raw_flux_min_max = get_flux_min_max(
        df=df,
        model_time_range_indices=model_time_range_indices,
        model_timestep=model_timestep,
    )
    # currently filtering based on flux, not concentration
    model_filter_range = return_valid_df_filter_range(
        user_filter_range=user_filter_range
    )

    # builds a map between model terminology and request_dict lists
    mapping = {}

    # all graph nodes
    species = set()

    for reaction in reactions:
        # logger.info(f"reaction {reaction}")
        if "reactants" in reaction:
            for reactant in reaction["reactants"]:
                species.add(reactant)
        
        # Currently, the following code will leave "adjustment" products,
        # like from wall-loss and emmissions calculations, floating.
        # If desired, the concentration/flux could simply be added to
        # the graphed values, but careful consideration of what is
        # a product and what is a reactant would be nescessary
        irr = None
        for product in reaction["products"]:
            if "irr__" not in product:
                species.add(product)
            else:
                irr = product
                logger.info(f"irr = product {irr}")
        if "reactants" in reaction:
            reactants = [
                f"{'' if v.get('qty') is None or v.get('qty') == 1 else v['qty']}{k}"
                for k, v in reaction["reactants"].items()
            ]
        products = [
            f"{'' if v.get('yield') is None or v.get('yield') == 1 or k.startswith('irr') else str(v['yield'])}{k}"
            for k, v in reaction["products"].items()
            if not k.startswith("irr")
        ]
        label = " + ".join(reactants) + " -> " + " + ".join(products)
        reaction["label"] = label
        reaction["irr"] = irr
        mapping[irr] = [[x for x in df.columns if irr in x][0], label]

    net = Network(directed=True)
    net.force_atlas_2based(damping=0.9, overlap=1)

    # graphing is strongly time-bound by graph physics (the locating of nodes
    # according to a pseudo-gravity simulation). Physics runs each time, but
    # this can be optimized out if we store the full graph with locations,
    # but pyvis is not a good choice to develop this algo on.
    if user_disabled_physics:
        net.toggle_physics(False)
    logger.info(f"mapping {mapping}")

    # add the nodes for the reactions and species

    for species in species:
        net.add_node(species)

    for reaction in reactions:
        average_flux = get_flux(
            series=df[mapping[reaction["irr"]][0]],
            model_time_range_indices=model_time_range_indices,
            model_timestep=model_timestep,
        )
        if (
            average_flux > model_filter_range[0]
            and average_flux < model_filter_range[1]
        ) or user_filter_toggle:
            display_color = "#FF7F7F"
            if user_filter_toggle and not (
                average_flux > model_filter_range[0]
                and average_flux < model_filter_range[1]
            ):
                display_color = "#e0e0e0"
            net.add_node(
                reaction["label"], label=reaction["label"], color=display_color
            )
            if "reactants" in reaction:
                for reactant in reaction["reactants"]:
                    if reactant in user_blocked_species:
                        continue
                    display_color = "#94b8f8"
                    average_flux = get_flux(
                        series=df[mapping[reaction["irr"]][0]],
                        model_time_range_indices=model_time_range_indices,
                        model_timestep=model_timestep,
                    )
                    if user_filter_toggle and not (
                        average_flux > model_filter_range[0]
                        and average_flux < model_filter_range[1]
                    ):
                        display_color = "#e0e0e0"
                    width = (
                        reaction["reactants"][reactant].get("yield", 1)
                        * average_flux
                    )
                    displayWidth = scale_arrow_width(
                        width=width,
                        raw_flux_min_max=raw_flux_min_max,
                        display_min_max=[1, user_width_scaling],
                        user_arrow_scaling_type=user_arrow_scaling_type,
                    )
                    net.add_edge(
                        reactant,
                        reaction["label"],
                        width=displayWidth,
                        title="flux: " + str(width),
                        color=display_color,
                    )
                # logger.info(f"average_flux: {average_flux}")
            for product in reaction["products"]:
                display_color = "#FF7F7F"
                # reaction rate here is take as the last time entry from our
                # simulation result.
                # todo change flux calc for user selected time window
                if "irr__" not in product:
                    average_flux = get_flux(
                        series=df[mapping[reaction["irr"]][0]],
                        model_time_range_indices=model_time_range_indices,
                        model_timestep=model_timestep,
                    )
                    if user_filter_toggle and not (
                        average_flux > model_filter_range[0]
                        and average_flux < model_filter_range[1]
                    ):
                        display_color = "#e0e0e0"
                    width = (
                        reaction["products"][product].get("yield", 1)
                        * average_flux
                    )
                    displayWidth = scale_arrow_width(
                        width=width,
                        raw_flux_min_max=raw_flux_min_max,
                        display_min_max=[1, user_width_scaling],
                        user_arrow_scaling_type=user_arrow_scaling_type,
                    )
                    net.add_edge(
                        reaction["label"],
                        product,
                        width=displayWidth,
                        color=display_color,
                        title="flux: " + str(width),
                    )
                # logger.info(f"average_flux: {average_flux}")
    # for reaction in reactions:
    #     if "reactants" in reaction:
    #         for reactant in reaction["reactants"]:
    #             logger.info(f"reactant: {reactant}")

    # set the layout and show the graph
    graph_file = f"{uid}_flow_network.html"
    net.save_graph(graph_file)
    with open(graph_file, "r") as f:
        contents = f.read()
    os.remove(graph_file)
    user_interface_options = {}

    # in order to display time range for user, front end either can take from
    # props (using getAllConditions ) and do calcs on front end, or get populated
    # from backend. user_interface_options allows populating from backend.
    user_interface_options["timeRange"] = [
        model_time_range_indices[0] * model_timestep,
        model_time_range_indices[1] * model_timestep,
    ]
    user_interface_options["filterRange"] = model_filter_range

    logger.info(f"user_interface_options: {user_interface_options}")

    # TODO refactor to use django inbuilt (contents ends up inserted code-injection style)
    return contents, json.dumps(
        user_interface_options, indent=4, default=np_encoder
    )
