from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #все рейсы постранично
    url(r'^arhive/$', views.all_flight, name='arhiveflights'),
    #Список рейсов в таймокне
    url(r'^flights/$', views.flight_list, name='flight_list'),
    #окно для ИСГ (возможность удалить ошибочные рейсы)
    url(r'^isg/$', views.isg, name='isg'),
    #Подробности выбранного рейса
    url(r'^flight/(?P<id>[0-9]+)/$', views.flight_detail, name='flight_detail'),
    #Список стоек регистрации
    url(r'^checkins/$', views.checkin_list, name='checkin_list'),
    #Выбрать конкретную стойку
    url(r'^checkin/(?P<id>[0-9]+)/$', views.checkin, name='checkin'),
    #Список выходов
    url(r'^boards/$', views.board_list, name='board_list'),
    #Выбор конкретного выхода
    url(r'^board/(?P<id>[0-9]+)$', views.boardgate, name='boardgate'),
    #Список багажных лент
    url(r'^baggages/$', views.baggage_list, name='baggage_list'),
    #Выбор конкрентной багажной ленты
    url(r'^baggages/(?P<id>[0-9]+)$', views.baggage, name='baggage'),
    #Табло стойки
    url(r'^tablo/checkin/(?P<id>[0-9]+)/$', views.tablocheckin, name='tablocheckin'),
    #url(r'^tablo/tst/checkin/(?P<id>[0-9]+)/$', views.tsttablocheckin, name='tablocheckin'),
    #Табло посадки
    #Табло карусели багажа
    #Табло вылета
    url(r'^tablo/departures/$', views.tablodeparture, name='tablodeparture'),
    #Табло прилета
    #Табло досмотра
]