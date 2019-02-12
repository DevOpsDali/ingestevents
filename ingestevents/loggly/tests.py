from django.test import TestCase
from loggly.models import LogglyEvent

# Create your tests here.

class DataDogInsert(TestCase):

  def setUp(self):
    DD_API_KEY = os.environ.get('DD_API_KEY')
    DD_APP_KEY = os.environ.get('DD_APP_KEY')
    LogglyEvent.objects.create(
                          "alert_name": "DateTest",
                          "alert_name": "DateTest",
                          "edit_alert_link": "https://sample.loggly.com/alerts/edit/8188",
                          "source_group": "N/A",
                          "start_time": "Feb 16 10:41:40",
                          "end_time": "Feb 17 11:46:40",
                          "search_link": "https://sample.loggly.com/search/?terms=&source_group=&savedsearchid=112323&from=2015-03...",
                          "query": "* ",
                          "num_hits": 225,
                          "recent_hits": "",
                          "owner_username": "sample",
                          "owner_subdomain": "sample",
                          "owner_email": "pm@loggly.com"
      )

  def test_data_dog_post(self):
    

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