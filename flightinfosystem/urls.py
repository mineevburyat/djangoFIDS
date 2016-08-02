from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.all_flight, name='arhiveflights'),
    #Список рейсов в таймокне
    url(r'^flights$', views.flight_list, name='flight_list'),
    #Подробности выбранного рейса
    url(r'^flight/(?P<id>[0-9]+)/$', views.flight_detail, name='flight_detail'),
    #Список стоек регистрации
    url(r'^checkin/(?P<id>[0-9]+)/$', views.checkin, name='checkin'),
    #Выбрать конкретную стойку
    url(r'^checkins/$', views.checkin_list, name='checkin_list'),
    #Список выходов
    url(r'^boards/$', views.board_list, name='board_list'),
    #Выбор конкретного выхода
    url(r'^board/(?P<id>[0-9]+)$', views.boardgate, name='boardgate'),
    #Список багажных лент
    #Выбор конкрентной багажной ленты
    #Табло стойки
    url(r'^tablo/checkin/(?P<id>[0-9]+)/$', views.tablocheckin, name='tablocheckin'),
    #url(r'^tablo/tst/checkin/(?P<id>[0-9]+)/$', views.tsttablocheckin, name='tablocheckin'),
    #Табло посадки
    #Табло карусели багажа
    #Табло вылета
    #Табло прилета
    #Табло досмотра
]