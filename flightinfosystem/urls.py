from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.flight_list, name='flight_list'),
]