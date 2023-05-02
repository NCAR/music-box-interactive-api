from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import views

import api.controller as controller
import api.database_tools as db_tools
import api.response_models as response_models
import api.request_models as request_models

import logging

logger = logging.getLogger(__name__)


class LoadExample(views.APIView):
    @swagger_auto_schema(
        query_serializer=request_models.LoadExampleSerializer,
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.ExampleSerializer
            )
        }
    )
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        example = request.GET.dict()['example']
        _ = db_tools.get_user_or_start_session(request.session.session_key)

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
        logger.debug(f"Run status | session key: {request.session.session_key}")
        response_message = db_tools.get_run_status(request.session.session_key)
        logger.info(f"Run status | {response_message}")
        return JsonResponse(response_message, encoder=response_models.RunStatusEncoder)


class RunView(views.APIView):
    @swagger_auto_schema(
        query_serializer=request_models.RunSerializer,
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.PollingStatusSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            request.session.save()
        logger.info(f"Recieved run requst for session {request.session.session_key}")
        if controller.publish_run_request(request.session.session_key, request.data):
            response = {'status': response_models.RunStatus.WAITING}
        else:
            response = {'status': response_models.RunStatus.ERROR}
        return JsonResponse(response, encoder=response_models.RunStatusEncoder)


class CompressConfigurationView(views.APIView):
    @swagger_auto_schema(
        query_serializer=request_models.RunSerializer,
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.PollingStatusSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            request.session.save()
        logger.info(f"Recieved compress configuration request for session {request.session.session_key}")
        logger.info(f"Request: {request}")
        zipfile = controller.handle_compress_configuration(request.session.session_key, request.data)
        response = HttpResponse(zipfile, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="config.zip"'
        return response


class ExtractConfigurationView(views.APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description='Success',
                schema=response_models.PollingStatusSerializer
            )
        }
    )
    def post(self, request):
        if not request.session.session_key:
            request.session.save()
        logger.info(f"Recieved extract configuration request for session {request.session.session_key}")
        conditions, mechanism = controller.handle_extract_configuration(request.session.session_key, request.data)
        return JsonResponse({ 'conditions': conditions, 'mechanism': mechanism })

