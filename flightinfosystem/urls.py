from django.conf.urls import url
from . import views

urlpatterns = [
    #/fids/ - ссылка на корень приложения от сюда попадаем в нужные модули
    url(r'^$', views.index, name='index'),
    #/fids/arhive/ все рейсы постранично (архив рейсов)
    url(r'^arhive/$', views.all_flight, name='arhiveflights'),
    #/fids/flights/ Список рейсов в таймокне от текущего времени
    url(r'^flights/$', views.flight_list, name='flight_list'),
    #/fids/isg/ окно для ИСГ (список рейсов в таймокне с возможностью удалить ошибочные рейсы)
    url(r'^isg/$', views.isg, name='isg'),
    #Справки (фильтр обслуженных рейсов)
    url(r'^spravki/$', views.spravki, name='spravki'),
    #редактирование рейса справками (для совместимости - управление справками табло выдачи багажа и посадками)
    url(r'^spravki/(?P<id>[0-9]+)/$', views.spravki_edit, name='spravki_edit'),
    #/fids/flight/nnn/ Подробности конкретного рейса
    url(r'^flight/(?P<id>[0-9]+)/$', views.flight_detail, name='flight_detail'),

    #Администрирование количества стоек регистрации, выходов и багажных лент
    #Список стоек регистрации
    url(r'^checkins/$', views.checkin_list, name='checkin_list'),
    # Список выходов
    url(r'^boards/$', views.board_list, name='board_list'),
    # Список багажных лент
    url(r'^baggages/$', views.baggage_list, name='baggage_list'),

    #Рабочие места стоек, выхода и багажной ленты
    #Выбрать конкретную стойку
    url(r'^checkin/(?P<id>[0-9]+)/$', views.checkin, name='checkin'),
    #Выбор конкретного выхода
    url(r'^board/(?P<id>[0-9]+)/$', views.boardgate, name='boardgate'),
    #Выбор конкрентной багажной ленты
    url(r'^baggages/(?P<id>[0-9]+)/$', views.baggage, name='baggage'),

    #Табло отображения информации
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