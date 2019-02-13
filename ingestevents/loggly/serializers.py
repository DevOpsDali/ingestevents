from django.contrib.auth.models import User, Group
from rest_framework import serializers
from datetime import datetime
from .models import LogglyEvent
from rest_framework.exceptions import ErrorDetail

class LogglySerializer(serializers.ModelSerializer):
  def to_internal_value(self, data):
    detail = None
    errors = {}

    if not isinstance(data['recent_hits'], list):
      detail = ErrorDetail("Should be list", code="invalid")
      errors['recent_hits'] = detail
    else:
      data['recent_hits'] = ','.join(data['recent_hits'])
    
    try:
      datetime.strptime(data['start_time'], '%b %d %H:%M:%S')
    except ValueError as e:
      detail = ErrorDetail("Does not match expected date format", code="invalid")
      errors['start_time'] = detail
    
    try:
      datetime.strptime(data['end_time'], '%b %d %H:%M:%S')
    except ValueError as e:
      detail = ErrorDetail("Does not match expected date format", code="invalid")
      errors['end_time'] = detail

    if errors:
      raise serializers.ValidationError(errors)
    else:
      return super(LogglySerializer, self).to_internal_value(data)

  class Meta:
    model = LogglyEvent
    fields = ('alert_name', 'edit_alert_link', 'source_group', 'start_time', 'end_time', 'search_link', 'query', 'num_hits', 'recent_hits', 'owner_username','owner_subdomain','owner_email')