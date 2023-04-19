from rest_framework import status, views
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from shared.utils import beautifyReaction
from dashboard.database_tools import get_model_run

import logging

import plots.plot_setup as plot_setup
import pandas as pd

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)
logging.basicConfig(format='%(asctime)s - [DEBUG] %(message)s',
                    level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s - [ERROR!!] %(message)s',
                    level=logging.ERROR)

class GetPlotContents(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_PLOT_CONTENTS ******")
        if not request.session.session_key:
            request.session.save()
        get = request.GET
        prop = get['type']
        response = HttpResponse()
        response.write(plot_setup.plots_unit_select(prop))
        # get model run from session
        model_run = get_model_run(request.session.session_key)

        if '/output.csv' not in model_run.results:
            return response
        # get /output.csv file from model run
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        subs = plot_setup.direct_sub_props(prop, csv)
        subs.sort()
        if prop != 'compare':
            for i in subs:
                prop = beautifyReaction(plot_setup.sub_props_names(i))
                response.write('<a href="#" class="sub_p list-group-item \
                                list-group-item-action" subType="normal" id="'
                               + i + '">☐ ' + prop + "</a>")
        elif prop == 'compare':
            for i in subs:
                prop = beautifyReaction(plot_setup.sub_props_names(i))
                response.write('<a href="#" class="sub_p list-group-item \
                                list-group-item-action" subType="compare" id="'
                               + i + '">☐ ' + prop + "</a>")
        return response


class GetPlot(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_PLOT ******")
        model_run = get_model_run(request.session.session_key)
        if '/output.csv' not in model_run.results:
            return HttpResponseBadRequest('Bad format for plot request',
                                      status=405)
        if request.method == 'GET':
            props = request.GET['type']
            buffer = io.BytesIO()
            # run get_plot function
            if request.GET['unit'] == 'n/a':
                buffer = plot_setup.get_plot(request.session.session_key, props, False)
            else:
                buffer = plot_setup.get_plot(request.session.session_key, props, request.GET['unit'])
            return HttpResponse(buffer.getvalue(), content_type="image/png")
        return HttpResponseBadRequest('Bad format for plot request',
                                      status=405)


class GetBasicDetails(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_BASIC_DETAILS ******")
        if not request.session.session_key:
            request.session.save()
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        plot_property_list = [x.split('.')[0] for x in csv.columns.tolist()]
        plot_property_list = [x.strip() for x in plot_property_list]
        for x in csv.columns.tolist():
            if "myrate" in x:
                plot_property_list.append('RATE')
        context = {
            'plots_list': plot_property_list
        }
        logging.info("plots list: " + str(context))
        return JsonResponse(context)


class GetFlowDetails(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_FLOW_DETAILS ******")
        if not request.session.session_key:
            request.session.save()
        model = models.ModelRun.objects.get(uid=request.session.session_key)
        output_csv = StringIO(model.results['/output.csv'])
        csv = pd.read_csv(output_csv, encoding='latin1')
        concs = [x for x in csv.columns if 'CONC' in x]
        species = [x.split('.')[1] for x in concs if 'myrate' not in x]

        step_length = 0
        if csv.shape[0] - 1 > 2:
            step_length = int(csv['time'].iloc[1])
        context = {
            "species": species,
            "stepVal": step_length,
            "simulation_length": int(csv['time'].iloc[-1])
        }
        logging.debug("returning basic info:" + str(context))
        return JsonResponse(context)


class GetFlow(views.APIView):
    def get(self, request):
        logging.info("****** GET request received GET_FLOW ******")
        if not request.session.session_key:
            request.session.save()
        logging.info(f"session id: {request.session.session_key}")
        logging.info("using data:" + str(request.GET.dict()))
        path_to_template = os.path.join(
            settings.BASE_DIR,
            "dashboard/templates/network_plot/flow_plot.html")
        flow = generate_flow_diagram(request.GET.dict(), request.session.session_key, path_to_template)
        return HttpResponse(flow)


class PlotSpeciesView(views.APIView):
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        if 'name' not in request.GET:
            return HttpResponseBadRequest("missing species name")
        species = request.GET['name']
        network_plot_dir = os.path.join(
                settings.BASE_DIR, "dashboard/templates/network_plot/" +
                request.session.session_key)
        template_plot = os.path.join(
            settings.BASE_DIR,
            "dashboard/templates/network_plot/plot.html")
        if not os.path.isdir(network_plot_dir):
            os.makedirs(network_plot_dir)
        # use copyfile()
        if exists(os.path.join(network_plot_dir, "plot.html")) is False:
            # create plot.html file if doesn't exist
            f = open(os.path.join(network_plot_dir, "plot.html"), "w")
            logging.info("putting plot into file " + str(os.path.join(network_plot_dir, "plot.html")))
        shutil.copyfile(template_plot, network_plot_dir + "/plot.html")
        logging.info("generating plot and exporting to " + str(network_plot_dir + "/plot.html"))
        # generate network plot and place it in unique directory for user
        html = generate_database_network_plot(request.session.session_key,
                                       species,
                                       network_plot_dir + "/plot.html")
        #plot = ('network_plot/'
        #        + request.session.session_key
        #        + '/plot.html')
        plot = str(network_plot_dir + "/plot.html")[1:]
        #logging.info("[debug] rendering from " + plot)
        #return render(request, plot)
        #logging.info("returning html: " + str(html))
        return HttpResponse(html)