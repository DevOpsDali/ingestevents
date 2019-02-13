import os
from appconf import AppConf

class LogglyAppConfig(AppConf): #Stub for setting some initial config options
  DD_API_KEY = os.environ.get('DD_API_KEY')
  DD_APP_KEY = os.environ.get('DD_APP_KEY')

  DD_DEFAULT_TITLE = "Empty Title, something's wrong"
  DD_DEFAULT_TEXT = "Empty Text, something's wrong"

  #Set this once in case it changes
  DD_LOGGLY_TIME_FORMAT = '%b %d %H:%M:%S'
  
  #If True it will use the time from Loggly. If False sends local time to DataDog
  DD_INCLUDE_TIME = False if "DD_INCLUDE_TIME" not in os.environ else os.environ.get('DD_INCLUDE_TIME')
  #If True uses the Loggly start_time field. If False uses the end_time field
  DD_USE_START_TIME = True if "DD_USE_START_TIME" not in os.environ else os.environ.get('DD_USE_START_TIME')

  #Being somewhat unfamiliar with Loggly/DataDog it's hard to know how to map Loggly fields to DataDog
  #The idea being long term to have these control the default message that's generated, but for now they aren't used
  DD_INCLUDE_PRIORITY = False if "DD_INCLUDE_PRIORITY" not in os.environ else os.environ.get('DD_INCLUDE_PRIORITY')
  DD_INCLUDE_HOST = False if "DD_INCLUDE_HOST" not in os.environ else os.environ.get('DD_INCLUDE_HOST')
  DD_INCLUDE_TAGS = False if "DD_INCLUDE_TAGS" not in os.environ else os.environ.get('DD_INCLUDE_TAGS')
  DD_INCLUDE_ALERT_TYPE = False if "DD_INCLUDE_ALERT_TYPE" not in os.environ else os.environ.get('DD_INCLUDE_ALERT_TYPE')
  DD_INCLUDE_AGGREGATION_KEY = False if "DD_INCLUDE_AGGREGATION_KEY" not in os.environ else os.environ.get('DD_INCLUDE_AGGREGATION_KEY')
  DD_INCLUDE_SOURCE_TYPE_NAME = False if "DD_INCLUDE_SOURCE_TYPE_NAME" not in os.environ else os.environ.get('DD_INCLUDE_SOURCE_TYPE_NAME')
  
  class Meta:
    prefix = ''