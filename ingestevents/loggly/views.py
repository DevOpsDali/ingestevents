import json, sys, time, logging, uuid
#from django.shortcuts import render
#from django.http import Http404
#from django.db import connection
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

exit
logger = logging.getLogger('info')

@api_view(["POST", "GET"])
def loggly(request):
  body = None
  trace_id = None
  base_log_string = None
  error_string = {}
  trace_id = str(uuid.uuid4())
  base_log_string = f"{trace_id} - "

  logger.info(f"{base_log_string}Loggly Request received")
  try:
    body=json.loads(request.body.decode('utf-8')) #Ensure that the request is valid JSON
    data=JSONParser().parse(request)
  except json.JSONDecodeError as e:
    error_string = { "Error" : f"Request was not valid JSON" }
    logger.error(f"{base_log_string}Request was not valid JSON")
    logger.error(f"{base_log_string}" + request.body.decode('utf-8'))
    return JsonResponse(error_string, status=status.HTTP_400_BAD_REQUEST)
  except ValueError as e:
    error_string = { "Error" : f"Request was not valid JSON" }
    logger.error(f"{base_log_string}Request was not valid JSON")
    logger.error(f"{base_log_string}" + request.body.decode('utf-8'))
    return JsonResponse({error_string}, status=status.HTTP_400_BAD_REQUEST)
  except TypeError as e:
    error_string = { "Error" : f"Request was not valid a valid type" }
    logger.error(f"{base_log_string}Request was not valid JSON")
    logger.error(f"{base_log_string}" + request.body.decode('utf-8'))
    return JsonResponse(error_string, status=status.HTTP_400_BAD_REQUEST)  

  #Should likely setup some sort of check against the source of the POST data.
  #Couldn't be sure of what the loggly request is going to look like but possibly do something like:
  
  # if "KnownLogglyValue" not in HttpRequest.get_host(request):
  #   return(JsonResponse("", status=status.HTTP_403_FORBIDDEN))
  #

  #Check if data is valid
  serializer = LogglySerializer(data=data)
  if not serializer.is_valid(): #Ensure data is valid. If not return a list of errors
    logger.error(f"{base_log_string}Validation Error: {serializer.errors}")
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  else:
    logger.info(f"{base_log_string}Request Data: {json.dumps(body)}")
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
    event.save(base_log_string) #Save the event
    logger.info(f"{base_log_string}Event {event.id} saved to database")   
    send_to_datadog = DataDogThread(base_log_string)
    send_to_datadog.process_event(event) #Threaded call to Datadog so we can return a response to Loggly without a dependency
  return Response(status=status.HTTP_204_NO_CONTENT)
