from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from .models import LogglyEvent
from .apps import LogglyAppConfig

class LogglySerializer(serializers.ModelSerializer):
  
  # Define checking for types so we can do some initial data validation
  
  def check_str(self, object):
    if not isinstance(self.event_data[object], str):
      self.error_list[object] = ErrorDetail("Should be str", code="invalid")
    else:
      return True

  def check_int(self, object):
    if not isinstance(self.event_data[object], int):
      self.error_list[object] = ErrorDetail("Should be int", code="invalid")
    else:
      return True

  def check_list(self, object):
    if not isinstance(self.event_data[object], list):
      self.error_list[object] = ErrorDetail("Should be list", code="invalid")
    else:
      return True

  #Since we need to format the data before it gets sent to the DB we have to capture it and format it here
  def to_internal_value(self, data):
    self.error_list = {}
    self.event_data = data
    errors = {}

    self.check_str('alert_name')
    self.check_str('edit_alert_link')
    self.check_str('source_group')

    #Ensure our time stamps are string typed and in the expected format
    if self.check_str('start_time'):
      try:
        datetime.strptime(self.event_data['start_time'], settings.DD_LOGGLY_TIME_FORMAT)
      except ValueError as e:
        self.error_list['start_time'] = ErrorDetail("Does not match expected date format", code="invalid")

    if self.check_str('end_time'):
      try:
        datetime.strptime(self.event_data['end_time'], settings.DD_LOGGLY_TIME_FORMAT)
      except ValueError as e:
        self.error_list['end_time'] = ErrorDetail("Does not match expected date format", code="invalid")

    self.check_str('search_link')
    self.check_str('query')
    self.check_int('num_hits')
    self.check_str('owner_username')
    self.check_str('owner_subdomain')
    self.check_str('owner_email')

    # Convert this into a comma delimited string for storage.
    # Wasn't able to dig out what this field looks like when populated so this may be a bad strategy
    if self.check_list('recent_hits'):
      data['recent_hits'] = ','.join(data['recent_hits'])
    
    #If there are error send them all back
    if self.error_list:
      raise serializers.ValidationError(self.error_list)
    else:
      return super(LogglySerializer, self).to_internal_value(data)

  class Meta:
    model = LogglyEvent
    fields = ('alert_name', 'edit_alert_link', 'source_group', 'start_time', 'end_time', 'search_link', 'query', 'num_hits', 'recent_hits', 'owner_username','owner_subdomain','owner_email')