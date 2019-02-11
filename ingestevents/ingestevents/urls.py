from django.urls import path
from django.conf.urls import url
from loggly import views
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^loggly/',views.loggly)
]