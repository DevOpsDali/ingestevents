# from django.db import models

# # Create your models here.
import sys, time, os
from threading import Thread #Allow sending of data dog event as a thread
from datetime import datetime 

from datadog import initialize, api #Data dog imports for standard usage and error handling
from datadog.api.exceptions import ApiError, ApiNotInitialized
from django.core.exceptions import ValidationError

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.conf import settings
from appconf import AppConf
from django.db import connection

def start_new_thread(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator

class LogglyAppConfig(AppConf): #Stub for setting some initial config options
  DD_INCLUDE_TIME = True if "DD_INCLUDE_TIME" not in os.environ else os.environ.get('DD_INCLUDE_TIME')
  DD_INCLUDE_PRIORITY = False if "DD_INCLUDE_PRIORITY" not in os.environ else os.environ.get('DD_INCLUDE_PRIORITY')
  DD_INCLUDE_HOST = False if "DD_INCLUDE_HOST" not in os.environ else os.environ.get('DD_INCLUDE_HOST')
  DD_INCLUDE_TAGS = False if "DD_INCLUDE_TAGS" not in os.environ else os.environ.get('DD_INCLUDE_TAGS')
  DD_INCLUDE_ALERT_TYPE = False if "DD_INCLUDE_ALERT_TYPE" not in os.environ else os.environ.get('DD_INCLUDE_ALERT_TYPE')
  DD_INCLUDE_AGGREGATION_KEY = False if "DD_INCLUDE_AGGREGATION_KEY" not in os.environ else os.environ.get('DD_INCLUDE_AGGREGATION_KEY')
  DD_INCLUDE_SOURCE_TYPE_NAME = False if "DD_INCLUDE_SOURCE_TYPE_NAME" not in os.environ else os.environ.get('DD_INCLUDE_SOURCE_TYPE_NAME')
  DD_USE_START_TIME = True if "DD_USE_START_TIME" not in os.environ else os.environ.get('DD_USE_START_TIME')
  DD_API_KEY = os.environ.get('DD_API_KEY')
  DD_APP_KEY = os.environ.get('DD_APP_KEY')
  DD_DEFAULT_TITLE = "Empty Title, something's wrong"
  DD_DEFAULT_TEXT = "Empty Text, something's wrong"
  class Meta:
    prefix = ''

class LogglyEvent(models.Model):
  #Most of the model views are going to just be text, and the fields that should be something like a date aren't coming in in a valid timestamp format
  alert_name = models.TextField()
  edit_alert_link = models.TextField()
  source_group = models.TextField()
  start_time = models.TextField()
  end_time = models.TextField()
  search_link = models.TextField()
  query = models.TextField()
  num_hits = models.PositiveIntegerField()
  recent_hits = models.TextField(blank=True)
  owner_username = models.TextField()
  owner_subdomain = models.TextField()
  owner_email = models.TextField()

  #Return the ID as a string
  def __str__(self):
    return str(self.id)

  #Save the event. We're doing data validation/manipulation in the serializer before we get here.
  def save(self, *args, **kwargs):
    super(LogglyEvent, self).save(*args, **kwargs)

class DataDogThread(Thread):
  def __init__(self):
    #Initialize the object with valid defaults
    self.title = settings.DD_DEFAULT_TITLE #Required: using non-empty values just in case
    self.text = settings.DD_DEFAULT_TEXT # "   "
    self.date_happened = None
    self.priority = "normal"    
    self.host = None
    self.tags = []
    self.alert_type = "info"
    self.aggregation_key = None
    self.source_type_name = None
    self.status = False
    self.response = None
    super(DataDogThread, self).__init__()

  def generate_generic_event_data(self, event):
    status = False
    try:
      self.text = f'''Alert Source Group: {event.source_group}
                      Search Link {event.search_link}
                      Query: {event.query}
                      Owner: {event.owner_username} | {event.owner_email}
                      Number of Hits: {event.num_hits}
                      Update this alert: {event.edit_alert_link}'''
      if settings.DD_INCLUDE_TIME: ## Check for time inclusion
        self.format_date_happened(event)
      #Hard enforcing length of the string currently. It would likely be better to enforce internal limits on certain text fields instead depending on the data
      if len(self.text) > 4000: 
        self.text = self.text[:4000]
    except ValueError as e:
      raise ValueError('An error occured generating event data')
    finally:
      return status

  def format_date_happened(self, event): #Function to handle converting Loggly timestamp to Posix
    try:
      #Loggly gives us two time stamps to choose from. Using default if we haven't explicitly stated which one to use
      time_list = event.start_time.split(" ") if settings.DD_USE_START_TIME else event.end_time.split(" ") 
      
      #For some reason the year isn't included in the Loggly time stamps.
      #For now just assume it's the current year and insert it so we get a valid posix timestamps
      time_list.insert(2, datetime.strftime(datetime.now(), '%y'))
      date_object = datetime.strptime(" ".join(time_list), '%b %d %y %H:%M:%S')
      self.date_happened = int(time.mktime(date_object.timetuple()))
      status = True
    except ValueError as e:
      raise ValueError('A problem occured with converting the timestamp to POSIX')

  def known_event_type(self, event):
    pass

  def put_event(self, event):
    try:
      options = {
        'api_key': settings.DD_API_KEY,
        'app_key': settings.DD_APP_KEY
      }

      initialize(**options)

      self.response = api.Event.create(
                        title=self.title, 
                        text=self.text, 
                        date_happened=self.date_happened,
                        priority=self.priority,
                        host=self.host,
                        tags=self.tags,
                        alert_type=self.alert_type,
                        aggregation_key=self.aggregation_key,
                        source_type_name=self.source_type_name
                      )
    except ApiNotInitialized as e:
      print("Problem initializing the datadog API: {}".format(e))
      self.status = False
    except ValueError as e:
      print("Values for API key and/or APP key appear to be invalid")
      self.status = False
    except:
      print("Unhandled Error while trying to post to datadog: {}".format(sys.exc_info()[0]))
      self.status = False
    finally:
      if self.response:
        self.status = True
        LogglyEvent.objects.filter(id=event.id).delete() # Delete the record if processed successfully
        connection.close() #Have to manually close the connection as we're in a thread
        print("Event successfully processed and sent to DataDog")
    return self.status

  @start_new_thread #Make sure that this function runs in a new thread
  def process_event(self, event):
    try:
      if self.known_event_type(event): #Example stub for checking for a known event type for custom processing
        pass
      else: #If it's a generic alert we don't have custom processing for build a generic alert format
        self.title = event.alert_name if len(event.alert_name) < 100 else event.alert_name[:100] #Hard force the title to be under 100 characters
        self.generate_generic_event_data(event)
      self.put_event(event)
      self.status = True
    except:
      print("Unhandled Error while processing the event: {}".format(sys.exc_info()[0]))
      self.status = False
    return self.status