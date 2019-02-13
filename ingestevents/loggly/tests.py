import json
from django.conf import settings
from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse

from loggly.models import LogglyEvent, DataDogThread
from loggly.views import loggly

print("\n\n----------------------------------------")
class LogglyViewTest(TestCase):
  def setUp(self):
    #Should eventually load these from a JSON file
    self.good_object = {
      "alert_name": "ViewTest",
      "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
      "source_group": "N/A",
      "start_time": "Feb 12 22:41:40",
      "end_time": "Feb 12 22:46:40",
      "search_link": "https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
      "query": "* ",
      "num_hits": 225,
      "recent_hits": [],
      "owner_username": "sample",
      "owner_subdomain": "sample",
      "owner_email": "pm@loggly.com"
    }
    self.bad_recent_hits_object = {
      "alert_name": "ViewTest",
      "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
      "source_group": "N/A",
      "start_time": "Feb 12 22:41:40",
      "end_time": "Feb 12 22:46:40",
      "search_link": "https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
      "query": "* ",
      "num_hits": 225,
      "recent_hits": "",
      "owner_username": "sample",
      "owner_subdomain": "sample",
      "owner_email": "pm@loggly.com"
    }
    self.bad_date_object = {
      "alert_name": "ViewTest",
      "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
      "source_group": "N/A",
      "start_time": "February 12 22:41:40",
      "end_time": "February 12 22:46:40",
      "search_link": "https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
      "query": "* ",
      "num_hits": 225,
      "recent_hits": [],
      "owner_username": "sample",
      "owner_subdomain": "sample",
      "owner_email": "pm@loggly.com"
    }


  def test_empty_request(self):
    response = self.client.post(reverse('loggly'))
    self.assertEqual(response.status_code, 400)

  def test_bad_date(self):
    response = self.client.post(reverse('loggly'), json.dumps(self.bad_date_object), content_type="application/json")
    self.assertEqual(response.status_code, 400)
  
  def test_bad_recent_hits(self):
    response = self.client.post(reverse('loggly'), json.dumps(self.bad_recent_hits_object), content_type="application/json")
    self.assertEqual(response.status_code, 400)
      
  def test_good_request(self):
    response = self.client.post(reverse('loggly'), json.dumps(self.good_object), content_type="application/json")
    self.assertEqual(response.status_code, 204)

class DataDogUnitTests(TransactionTestCase):
  def setUp(self):
    #Should eventually load these from a JSON file
    self.good_event_object = LogglyEvent.objects.create(
        alert_name="UnitTestAlert",
        edit_alert_link="https://sample.loggly.com/alerts/edit/0000000000",
        source_group="N/A",
        start_time="Feb 12 22:41:40",
        end_time="Feb 12 22:46:40",
        search_link="https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
        query="*",
        num_hits=10,
        recent_hits="",
        owner_username="Mr. UnitTest",
        owner_subdomain="Testing",
        owner_email="pm@nowhere"
      )
    self.bad_date_object = LogglyEvent.objects.create(
        alert_name="UnitTestAlert",
        edit_alert_link="https://sample.loggly.com/alerts/edit/000000000",
        source_group="N/A",
        start_time="February 12 10:41:40",
        end_time="February 12 11:46:40",
        search_link="https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
        query="*",
        num_hits=1000,
        recent_hits="",
        owner_username="Mr.UnitTest",
        owner_subdomain="Testing",
        owner_email="pm@loggly.com"
      )

  #Test that a class object with just the defaults is properly sent
  def test_datadog_class_object(self):

    test_datadog_class_object = DataDogThread()
    self.assertTrue(test_datadog_class_object.put_event(self.good_event_object))

  #Test a good object is generated and inserted as expected
  def test_datadog_insert_of_good_event(self):
    test_datadog_insert_of_good_event = DataDogThread() 
    test_datadog_insert_of_good_event.generate_generic_event_data(self.good_event_object)
    self.assertTrue(test_datadog_insert_of_good_event.put_event(self.good_event_object))

  #Ensure a badly formatted timestamp in the database is caught when posting to DataDog
  def test_datadog_insert_of_bad_date(self):
    test_datadog_insert_of_bad_date = DataDogThread() 
    self.assertFalse(test_datadog_insert_of_bad_date.generate_generic_event_data(self.bad_date_object))
  
  #Ordering of tests 
  #Make sure an error is raised if the DataDog API/APP keys aren't correct
  def test_unset_keys(self):
    temp_api_key = settings.DD_API_KEY
    temp_app_key = settings.DD_APP_KEY
    settings.DD_API_KEY = ""
    settings.DD_APP_KEY = ""
    test_unset_keys = DataDogThread()
    test_unset_keys.generate_generic_event_data(self.good_event_object)
    self.assertFalse(test_unset_keys.put_event(self.good_event_object))
    settings.DD_API_KEY = temp_api_key
    settings.DD_APP_KEY = temp_app_key

  #Make sure an error is raised if the DataDog API/APP keys aren't correct
  def test_bad_keys(self):
    temp_api_key = settings.DD_API_KEY
    temp_app_key = settings.DD_APP_KEY
    settings.DD_API_KEY = "asdfq2394o8aesdfasdf"
    settings.DD_APP_KEY = "asdasdf23fjhq23948asdflkjasdf"
    test_bad_keys = DataDogThread()
    test_bad_keys.generate_generic_event_data(self.good_event_object)
    self.assertFalse(test_bad_keys.put_event(self.good_event_object))
    settings.DD_API_KEY = temp_api_key
    settings.DD_APP_KEY = temp_app_key

  def teardown(self):
    self.bad_date_object.delete()
    self.good_event_object.delete()


# {
#   "alert_name": "DateTest",
#   "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
#   "source_group": "N/A",
#   "start_time": "Feb 16 10:41:40",
#   "end_time": "Feb 17 11:46:40",
#   "search_link": "https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
#   "query": "* ",
#   "num_hits": 225,
#   "recent_hits": [],
#   "owner_username": "sample",
#   "owner_subdomain": "sample",
#   "owner_email": "pm@loggly.com"
# }