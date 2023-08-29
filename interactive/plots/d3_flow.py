from io import StringIO
import api.models
import numpy as np
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


def return_valid_df_time_indices(df, user_time_range, model_timestep):
    """time interval should be in format [small, large]
    and have a minimum difference greater than or equal to the model timestep
    """

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


def return_valid_df_filter_range(user_filter_range):
    """Simple logic check on user inputed time range
    to ensure that it is in format [small, large]
    """
    if user_filter_range[0] < user_filter_range[1]:
        return user_filter_range
    else:
        return [0, 1000000]


def get_flux_array(series, model_time_indices, model_timestep):
    """get flux returns the sum of the differences between each timestep
    divided by the length of the array
    divided by the size of the timestep.
    Resultant units should be (change in concentration)/time
    """
    series_diff = np.diff(
        series[model_time_indices[0] : model_time_indices[1] + 1]
    )
    return series_diff / model_timestep


def generate_D3_flow_diagram(request_dict, uid):
    """Main function grabs model data and user settings, and returns an
    html file with the graph, and json with the adjusted user settings
    """
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

    user_time_range = [request_dict["startStep"], request_dict["endStep"]]

    reactions = request_dict["reactions"]["reactions"]

    #######################################################
    # process user selections to use with modeling results:
    #######################################################
    model_time_indices = return_valid_df_time_indices(
        df=df, user_time_range=user_time_range, model_timestep=model_timestep
    )
    # for use with display_width calculation.

    # builds a map between model terminology and request_dict lists
    mapping = {}

    # all graph nodes
    species = set()

    reactionGraph = {}
    reactionGraph["nodes"] = []
    reactionGraph["links"] = []

    for reaction in reactions:
        if "reactants" in reaction:
            for reactant in reaction["reactants"]:
                if reactant not in species:
                    reactionGraph["nodes"].append(
                        {"type": "reactant", "id": reactant, "group": 1}
                    )
                species.add(reactant)

        # Currently, the following code will leave "adjustment" products,
        # like from wall-loss and emmissions calculations, floating.
        # If desired, the concentration/flux could simply be added to
        # the graphed values, but careful consideration of what is
        # a product and what is a reactant would be nescessary
        irr = None
        for product in reaction["products"]:
            if "irr__" not in product:
                if product not in species:
                    reactionGraph["nodes"].append(
                        {"type": "product", "id": product, "group": 1}
                    )
                species.add(product)
            else:
                irr = product
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

    # add the nodes for the reactions and species

    for reaction in reactions:
        if reaction["label"] not in species:
            reactionGraph["nodes"].append(
                {"type": "processes", "id": reaction["label"], "group": 3}
            )
        species.add(reaction["label"])
        if "reactants" in reaction:
            for reactant in reaction["reactants"]:
                reactionGraph["links"].append(
                    {
                        "source": reactant,
                        "target": reaction["label"],
                        "name": "flux: ",
                        "rawFlux": 0.9,
                        "showLink": True,
                        "rawFluxArray": list(
                            get_flux_array(
                                series=df[mapping[reaction["irr"]][0]],
                                model_time_indices=model_time_indices,
                                model_timestep=model_timestep,
                            )
                        ),
                        "stoichiometricCoefficient": reaction["reactants"][
                            reactant
                        ].get("yield", 1),
                    }
                )
        for product in reaction["products"]:
            if "irr__" not in product:
                reactionGraph["links"].append(
                    {
                        "source": reaction["label"],
                        "target": product,
                        "name": "flux: ",
                        "rawFlux": 0.9,
                        "showLink": True,
                        "rawFluxArray": list(
                            get_flux_array(
                                series=df[mapping[reaction["irr"]][0]],
                                model_time_indices=model_time_indices,
                                model_timestep=model_timestep,
                            )
                        ),
                        "stoichiometricCoefficient": reaction["products"][
                            product
                        ].get("yield", 1),
                    }
                )

    # set the layout and show the graph

    user_interface_options = {}

    # in order to display time range for user, front end either can take from
    # props (using getAllConditions ) and do calcs on front end, or get populated
    # from backend. user_interface_options allows populating from backend.
    user_interface_options["timeStep"] = model_timestep
    user_interface_options["timeRange"] = list(model_time_indices)
    user_interface_options["species"] = list(species)
    user_interface_options["graphInfo"] = reactionGraph
    contents = "</html>"
    logger.info(f"timeRange, {user_interface_options['timeRange']}")
    # TODO refactor to use django inbuilt (contents ends up inserted code-injection style)
    return (
        contents,
        json.dumps(user_interface_options, indent=4, default=np_encoder),
    )
