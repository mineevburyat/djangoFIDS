from django.conf.urls import url
from . import views

urlpatterns = [
    #Список рейсов в таймокне
    url(r'^$', views.flight_list, name='flight_list'),
    #Подробности выбранного рейса
    url(r'^flight/(?P<id>[0-9]+)/$', views.flight_detail, name='flight_detail'),
    #Список стоек регистрации
    url(r'^checkin/(?P<id>[0-9]+)/$', views.checkin, name='checkin'),
    #Выбрать конкретную стойку
    url(r'^checkin/$', views.checkin_list, name='checkin_list'),
    #Список выходов
    url(r'^boards/$', views.board_list, name='board_list'),
    #Выбор конкретного выхода
    #Список багажных лент
    #Выбор конкрентной багажной ленты
    #Табло стойки
    url(r'^tablo/checkin/(?P<id>[0-9]+)/$', views.tablocheckin, name='tablocheckin'),
    #Табло посадки
    #Табло карусели багажа
    #Табло вылета
    #Табло прилета
    #Табло досмотра
]