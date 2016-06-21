from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.flight_list, name='flight_list'),
    url(r'^flight/(?P<id>[0-9]+)/$', views.flight_detail, name='flight_detail'),
    url(r'^checkin/$', views.checkin_list, name='checkin_list.html'),
    url(r'^checkin/(?P<id>[0-9]+)/$', views.check, name='checkin.html'),
]