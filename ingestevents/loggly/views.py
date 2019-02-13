import json, sys, time
from django.shortcuts import render
from django.http import Http404
from django.db import connection
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpRequest

from .models import LogglyEvent, DataDogThread
from .serializers import LogglySerializer

@api_view(["POST", "GET"])
def loggly(request):
  status_code = 500
  body = None
  try:
    body=json.loads(request.body.decode('utf-8')) #Ensure that the request is valid JSON
    data=JSONParser().parse(request)
  except ValueError as e:
    return JsonResponse({"Error": "Request contained invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
  
  #Should likely setup some sort of check against the source of the POST data.
  #Couldn't be sure of what the loggly request is going to look like but possibly do something like:
  
  # if "KnownLogglyValue" not in HttpRequest.get_host(request):
  #   return(JsonResponse("", status=status.HTTP_403_FORBIDDEN))
  #
  

  #Check if data is valid
  serializer = LogglySerializer(data=data)
  if not serializer.is_valid(): #Ensure data is valid. If not return a list of errors
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  else:
    event = LogglyEvent( #Ingest the json event and pass to the model
            alert_name=body['alert_name'], 
            edit_alert_link=body['edit_alert_link'],
            source_group=body['source_group'], 
            start_time = body['start_time'],  #Store start and end time as strings as they aren't standard and we're going to have to convert to posix later anyway.
            end_time = body['end_time'], 
            search_link = body['search_link'], 
            query = body['query'], 
            num_hits = body['num_hits'], 
            recent_hits = body['recent_hits'], #Unable to find formatting of this in the loggly docs. Join into a string and just save it
            owner_username = body['owner_username'], 
            owner_subdomain = body['owner_subdomain'], 
            owner_email = body['owner_email'])
    event.save() #Save the event
    status_code = 204
    send_to_datadog = DataDogThread() #Threaded call to Datadog so we can return a response to Loggly
    send_to_datadog.process_event(event)
  return Response(status=status_code)
