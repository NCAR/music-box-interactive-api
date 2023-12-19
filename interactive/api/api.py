from django.http import HttpResponse, JsonResponse, FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views
import json

import shared.configuration_utils as config_utils
import api.controller as controller
import api.response_models as response_models
import api.request_models as request_models

import logging

logger = logging.getLogger(__name__)


class LoadExample(views.APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='example',
                in_=openapi.IN_QUERY,
                description='The example to load',
                type=openapi.TYPE_STRING,
                # use the Enum values
                enum=[e.value for e in request_models.Example]
            )
        ],
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.ConfigSerializer
            )
        }
    )
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        example = request.GET.dict()['example']
        conditions, mechanism = controller.load_example(example)
        return JsonResponse({'conditions': conditions, 'mechanism': mechanism})


class RunStatusView(views.APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.PollingStatusSerializer
            )
        }
    )
    def get(self, request):
        logger.debug(
            f"Run status | session key: {request.session.session_key}")
        response = controller.get_run_status(request.session.session_key)
        logger.info(f"Run status | {response}")
        return JsonResponse(response, encoder=response_models.RunStatusEncoder)


class RunView(views.APIView):
    @swagger_auto_schema(
        query_serializer=request_models.ConfigSerializer,
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.PollingStatusSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            logger.debug("Saving new session")
            request.session.save()
        logger.debug(
            f"Run request | session key: {request.session.session_key}")
        controller.publish_run_request(
            request.session.session_key,
            request.data['config'])
        response = controller.get_run_status(request.session.session_key)
        return JsonResponse(response, encoder=response_models.RunStatusEncoder)


class LoadResultsView(views.APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Success',
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            )
        }
    )
    def get(self, request):
        logger.debug(
            f"load results | session key: {request.session.session_key}")
        response = controller.get_results_file(
            request.session.session_key).to_dict(
            orient='list')
        return JsonResponse(response)


class CompressConfigurationView(views.APIView):
    @swagger_auto_schema(
        request_body=request_models.ConfigSerializer,
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.FileSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            logger.debug("Saving new session")
            request.session.save()
        logger.info(
            f"Recieved compress configuration request for session {request.session.session_key}")
        config = json.loads(request.body)['config']
        zipfile = controller.handle_compress_configuration(
            request.session.session_key, config)
        response = FileResponse(zipfile)
        config_utils.remove_zip_folder(request.session.session_key)
        return response


class ExtractConfigurationView(views.APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type='object',
            properties={
                'file': openapi.Schema(type='string', format='binary'),
            },
            required=['file']
        ),
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.ConfigSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            logger.debug("Saving new session")
            request.session.save()
        logger.info(
            f"Recieved extract configuration request for session {request.session.session_key}")
        conditions, mechanism = controller.handle_extract_configuration(
            request.session.session_key, request.FILES["file"])
        config_utils.remove_session_folder(request.session.session_key)
        return JsonResponse({'conditions': conditions, 'mechanism': mechanism})


class DownloadResultsView(views.APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.FileSerializer
            )
        }
    )
    def get(self, request):
        logger.info(
            f"Received download results request for session {request.session.session_key}")
        results = controller.get_results_file(request.session.session_key)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=output.csv'
        results.to_csv(path_or_buf=response, index=False)
        return response
