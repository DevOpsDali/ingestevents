import json, logging
from django.conf import settings
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse

from loggly.models import LogglyEvent, DataDogThread
from loggly.views import loggly

logger = logging.getLogger('info')
logging.disable(logging.CRITICAL)

class LogglyViewTest(TestCase):
  def setUp(self):
    #Should eventually load these from a JSON file
    self.good_object = {
      "alert_name": "GoodViewTestObject",
      "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
      "source_group": "N/A",
      "start_time": "Feb 12 22:41:40",
      "end_time": "Feb 12 22:46:40",
      "search_link": "https://nowhere.com",
      "query": "*",
      "num_hits": 225,
      "recent_hits": [],
      "owner_username": "GoodUnitTest",
      "owner_subdomain": "sample",
      "owner_email": "pm@loggly.com"
    }
    self.bad_date_object = {
      "alert_name": "BadDateObject",
      "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
      "source_group": "N/A",
      "start_time": "February 12 22:41:40",
      "end_time": "February 12 22:46:40",
      "search_link": "https://nowhere.com",
      "query": "*",
      "num_hits": 225,
      "recent_hits": [],
      "owner_username": "BadDateUnitTest",
      "owner_subdomain": "sample",
      "owner_email": "pm@loggly.com"
    }
    self.bad_types_object = {
      "alert_name": [],
      "edit_alert_link": [],
      "source_group": 123,
      "start_time": 123,
      "end_time": 123,
      "search_link": [],
      "query": [],
      "num_hits": "225",
      "recent_hits": 123,
      "owner_username": 123,
      "owner_subdomain": 123,
      "owner_email": 123
    }

  def test_empty_request(self):
    print("test_empty_request")
    response = self.client.post(reverse('loggly'))
    self.assertEqual(response.status_code, 400)

  def test_bad_dates(self):
    print("test_bad_dates")
    response = self.client.post(reverse('loggly'), json.dumps(self.bad_date_object), content_type="application/json")
    self.assertEqual(response.status_code, 400)
  
  def test_bad_types(self):
    print("test_bad_types")
    response = self.client.post(reverse('loggly'), json.dumps(self.bad_types_object), content_type="application/json")
    self.assertIn(b'"alert_name": "Should be str"', response.content)
    self.assertIn(b'"edit_alert_link": "Should be str"', response.content)
    self.assertIn(b'"source_group": "Should be str"', response.content)
    self.assertIn(b'"start_time": "Should be str"', response.content)
    self.assertIn(b'"end_time": "Should be str"', response.content)
    self.assertIn(b'"search_link": "Should be str"', response.content)
    self.assertIn(b'"query": "Should be str"', response.content)
    self.assertIn(b'"num_hits": "Should be int"', response.content)
    self.assertIn(b'"owner_username": "Should be str"', response.content)
    self.assertIn(b'"owner_subdomain": "Should be str"', response.content)
    self.assertIn(b'"owner_email": "Should be str"', response.content)
    self.assertIn(b'"recent_hits": "Should be list"', response.content)
    self.assertEqual(response.status_code, 400)
      
  def test_good_request(self):
    print("test_good_request")
    response = self.client.post(reverse('loggly'), json.dumps(self.good_object), content_type="application/json")
    self.assertEqual(response.status_code, 204)

class DataDogUnitTests(TransactionTestCase):
  def setUp(self):
    #Should eventually load these from a JSON file
    self.test_id="aaaaaaaa-1111-2222-3333-zzzzzzzzzzzz"
    self.good_event_object = LogglyEvent.objects.create(
        alert_name="GoodUnitTestAlert",
        edit_alert_link="https://sample.loggly.com/alerts/edit/0000000000",
        source_group="N/A",
        start_time="Feb 12 22:41:40",
        end_time="Feb 12 22:46:40",
        search_link="https://nowhere.com",
        query="*",
        num_hits=10,
        recent_hits="",
        owner_username="GoodUnitTest",
        owner_subdomain="Testing",
        owner_email="noone@nowhere"
      )
    self.bad_date_object = LogglyEvent.objects.create(
        alert_name="BadUnitTestAlert",
        edit_alert_link="https://sample.loggly.com/alerts/edit/000000000",
        source_group="N/A",
        start_time="February 12 10:41:40",
        end_time="February 12 11:46:40",
        search_link="https://nowhere.com",
        query="*",
        num_hits=1000,
        recent_hits="",
        owner_username="BadUnitTest",
        owner_subdomain="Testing",
        owner_email="pm@loggly.com"
      )

  #Test that a class object with just the defaults is properly sent
  def test_datadog_class_object(self):
    print("test_datadog_class_object")
    test_datadog_class_object = DataDogThread(self.test_id)
    self.assertTrue(test_datadog_class_object.put_event(self.good_event_object))

  #Test a good object is generated and inserted as expected
  def test_datadog_insert_of_good_event(self):
    print("test_datadog_insert_of_good_event")
    test_datadog_insert_of_good_event = DataDogThread(self.test_id) 
    test_datadog_insert_of_good_event.title = self.good_event_object.alert_name
    test_datadog_insert_of_good_event.text = f'''Alert Source Group: {self.good_event_object.source_group}
                    Search Link {self.good_event_object.search_link}
                    Query: {self.good_event_object.query}
                    Owner: {self.good_event_object.owner_username} | {self.good_event_object.owner_email}
                    Number of Hits: {self.good_event_object.num_hits}
                    Update this alert: {self.good_event_object.edit_alert_link}'''
    self.assertTrue(test_datadog_insert_of_good_event.put_event(self.good_event_object))

  #Ensure a badly formatted timestamp in the database is caught when posting to DataDog
  def test_datadog_insert_of_bad_date(self):
    print("test_datadog_insert_of_bad_date")
    test_datadog_insert_of_bad_date = DataDogThread(self.test_id) 
    self.assertFalse(test_datadog_insert_of_bad_date.generate_generic_event_data(self.bad_date_object))
  
  #Make sure an error is raised if the DataDog API/APP keys aren't correct
  def test_unset_keys(self):
    print("test_unset_keys")
    temp_api_key = settings.DD_API_KEY
    temp_app_key = settings.DD_APP_KEY
    settings.DD_API_KEY = ""
    settings.DD_APP_KEY = ""
    test_unset_keys = DataDogThread(self.test_id)
    test_unset_keys.generate_generic_event_data(self.good_event_object)
    self.assertFalse(test_unset_keys.put_event(self.good_event_object))
    settings.DD_API_KEY = temp_api_key
    settings.DD_APP_KEY = temp_app_key    

  #Make sure an error is raised if the DataDog API/APP keys aren't correct
  def test_bad_datadog_keys(self):
    print("test_bad_datadog_keys")
    temp_api_key = settings.DD_API_KEY
    temp_app_key = settings.DD_APP_KEY
    settings.DD_API_KEY = "asdfq2394o8aesdfasdf"
    settings.DD_APP_KEY = "asdasdf23fjhq23948asdflkjasdf"
    test_bad_datadog_keys = DataDogThread(self.test_id)
    test_bad_datadog_keys.generate_generic_event_data(self.good_event_object)
    self.assertFalse(test_bad_datadog_keys.put_event(self.good_event_object))
    settings.DD_API_KEY = temp_api_key
    settings.DD_APP_KEY = temp_app_key

  def teardown(self):
    self.bad_date_object.delete()
    self.good_event_object.delete()