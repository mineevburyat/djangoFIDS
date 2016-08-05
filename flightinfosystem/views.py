import datetime
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Flight, Checkin, FlightStatus, EventLog, Board, Baggege

def index(request):
    return render(request, 'flightinfosystem/index.html', {})

def all_flight(request):
    flight_all = Flight.objects.all()
    paginator = Paginator(flight_all, 30)  # Show 30 flights per page
    page = request.GET.get('page')
    try:
        flights = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        flights = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        flights = paginator.page(paginator.num_pages)
    return render_to_response('flightinfosystem/arhiveflights.html', {"flights": flights})

def flight_list(request, past=7, future=24):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    flights = Flight.objects.filter(timeplan__lt=futuretime).filter(timeplan__gt=pasttime).order_by('timeplan')
    return render(request, 'flightinfosystem/flight_list.html', {'flights': flights})

def flight_detail(request, id):
    flight = get_object_or_404(Flight, id=id)
    flightstatus = FlightStatus.objects.get(fly=flight)
    event = EventLog.objects.filter(fly=flight)
    return render(request, 'flightinfosystem/flight_detail.html', {'flight': flight,
                                                                   'flightstatus': flightstatus,
                                                                   'flightevent': event})

def checkin_list(request):
    checkins = Checkin.objects.all()
    return render(request, 'flightinfosystem/checkin_list.html', {'checkins': checkins})

def checkin(request, id, past=11, future=20):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    check = get_object_or_404(Checkin, id=id)
    if request.method == 'GET':
        if check.checkinfly is None:
            # Если стойка не привязана к рейсу, то
            # Отобразить вылетающие рейсы в временном окне, и предоставить возможность выбора рейса
            departureflight = Flight.objects.filter(ad=0).filter(timeplan__lt=futuretime).filter(
                timeplan__gt=pasttime).order_by('timeplan')
            return render(request, 'flightinfosystem/checkin-select.html', {'check': check,
                                                                            'depart': departureflight})
        else:
            #Отобразить статусы рейса прикрепленного к стойке и возможность закрыть регистрацию на стойке
            flight = check.checkinfly
            flightstatus = FlightStatus.objects.get(fly=flight)
            event = EventLog.objects.filter(fly=flight)
            return render(request, 'flightinfosystem/checkin-status.html',
                          {'flightevent': event, 'flight': flight, 'flightstatus': flightstatus, 'check': check})
    elif request.method == 'POST':
        flightid = request.POST['id']
        url = request.path
        if check.checkinfly is None:
            # Стойка не привязана к рейсу. Привязать. Внести данные в flightstat и eventlog
            # и переслать на страницу стойки
            selectflight = get_object_or_404(Flight, id=flightid)
            flightstatus = FlightStatus.objects.get(fly=selectflight)
            if not flightstatus.checkin:
                #Если регистрация не открыта, то поднять флаг и сгенерировать событие
                flightstatus.checkin = True
                flightstatus.save()
                text = 'стойка ' + check.shortname + ' ' + check.num
                eventlog = EventLog(fly=selectflight, event_id=4, descript=text)
                eventlog.save()
            else:
                #Если регистрация идет, то сгенерировать событие о добавлении
                text = 'стойка ' + check.shortname + ' ' + check.num
                eventlog = EventLog(fly=selectflight, event_id=5, descript=text)
                eventlog.save()
            #привязать стойку к рейсу
            check.checkinfly = selectflight
            check.classcheckin = request.POST['class']
            check.save()
            return redirect(url, id=check.id)
        else:
            # отвязать стойку от рейса, проверить есть ли еще стойки с привязанным рейсом,
            # если нет, то сменить статус рейса, создать события
            check.checkinfly = None
            check.save()
            text = check.shortname + ' №' + check.num
            fly = Flight.objects.get(id=int(request.POST['id']))
            checkinlist = Checkin.objects.filter(checkinfly=fly)
            if len(checkinlist) == 0:
                flightstatus = FlightStatus.objects.get(fly=fly)
                flightstatus.checkinstop = True
                flightstatus.save()
                text = check.shortname + ' ' + check.num
                eventlog = EventLog(fly=fly, event_id=6, descript=text)
                eventlog.save()
                eventlog = EventLog(fly=fly, event_id=7, descript=text)
                eventlog.save()
            else:
                eventlog = EventLog(fly=fly, event_id=6, descript=text)
                eventlog.save()
            return redirect(request.path, id=check.id)

def board_list(request):
    boardsgate = Board.objects.all()
    return render(request, 'flightinfosystem/board_list.html', {'boards': boardsgate})

def boardgate(request, id, past=11, future=11):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    boardgt = get_object_or_404(Board, id=id)
    if request.method == 'GET':
        if boardgt.boardfly is None:
            # Выход не привязан к рейсу, то
            # Отобразить вылетающие рейсы со статусом регистрация и регистрация закрыта
            # в временном окне, и предоставить возможность выбора рейса
            checkinflight = Flight.objects.filter(ad=0).filter(timeplan__lt=futuretime).\
                filter(timeplan__gt=pasttime).order_by('timeplan')
            return render(request, 'flightinfosystem/board-select.html', {'boardgate': boardgt,
                                                                          'depart': checkinflight})
        else:
            # Отобразить статусы рейса прикрепленного к выходу и возможность закрыть посадку пассажиров
            flight = boardgt.boardfly
            flightstatus = FlightStatus.objects.get(fly=flight)
            event = EventLog.objects.filter(fly=flight)
            return render(request, 'flightinfosystem/board-status.html',
                              {'flightevent': event, 'flight': flight, 'flightstatus': flightstatus, 'boardgate': boardgt})
    elif request.method == 'POST':
        flightid = request.POST['id']
        url = request.path
        if boardgt.boardfly is None:
            # Гейт не привязан к рейсу. Привязать. Внести данные в flightstat и eventlog
            # и переслать на страницу выхода
            selectflight = get_object_or_404(Flight, id=flightid)
            flightstatus = FlightStatus.objects.get(fly=selectflight)
            flightstatus.board = True
            flightstatus.save()
            text = boardgt.shortname + ' ' + boardgt.num
            eventlog = EventLog(fly=selectflight, event_id=8, descript=text)
            eventlog.save()
            boardgt.boardfly = selectflight
            boardgt.save()
            return redirect(url, id=boardgt.id)
        else:
            # отвязать гейт от рейса, сменить статус рейса, создать события
            boardgt.boardfly = None
            boardgt.save()
            text = boardgt.shortname + ' №' + boardgt.num
            fly = Flight.objects.get(id=int(request.POST['id']))
            flightstatus = FlightStatus.objects.get(fly=fly)
            flightstatus.board = False
            flightstatus.boardstop = True
            flightstatus.save()
            eventlog = EventLog(fly=fly, event_id=9, descript=text)
            eventlog.save()
            return redirect(request.path, id=boardgt.id)

def baggage_list(request):
    baggages = Baggege.objects.all()
    return render(request, 'flightinfosystem/baggage_list.html', {'baggages': baggages})

def baggage(request, id, past=11, future=11):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    bag = get_object_or_404(Baggege, id=id)
    if request.method == 'GET':
        if bag.baggagefly is None:
            # Карусель не привязана к рейсу, то
            # Отобразить прилетающие рейсы
            arriveflight = Flight.objects.filter(ad=1).order_by('timeplan')
            return render(request, 'flightinfosystem/baggage-select.html', {'baggage': bag,
                                                                          'arrive': arriveflight})
        else:
            # Отобразить статусы рейса прикрепленного к карусели
            #  и возможность закрыть выдачу багажа
            flight = bag.baggagefly
            flightstatus = FlightStatus.objects.get(fly=flight)
            event = EventLog.objects.filter(fly=flight)
            return render(request, 'flightinfosystem/baggage-status.html',
                              {'flightevent': event, 'flight': flight,
                               'flightstatus': flightstatus, 'baggage': bag})
    elif request.method == 'POST':
        flightid = request.POST['id']
        url = request.path
        if bag.baggagefly is None:
            # Карусель не привязана к рейсу. Привязать. Внести данные в flightstat и eventlog
            # и переслать на страницу выхода
            selectflight = get_object_or_404(Flight, id=flightid)
            flightstatus = FlightStatus.objects.get(fly=selectflight)
            flightstatus.baggage = True
            flightstatus.save()
            text = bag.shortname + ' ' + bag.num
            eventlog = EventLog(fly=selectflight, event_id=10, descript=text)
            eventlog.save()
            bag.baggagefly = selectflight
            bag.save()
            return redirect(url, id=bag.id)
        else:
            # отвязать карусель от рейса, сменить статус рейса, создать события
            bag.baggagefly = None
            bag.save()
            text = bag.shortname + ' №' + bag.num
            fly = Flight.objects.get(id=int(request.POST['id']))
            flightstatus = FlightStatus.objects.get(fly=fly)
            flightstatus.baggagestop = True
            flightstatus.save()
            eventlog = EventLog(fly=fly, event_id=11, descript=text)
            eventlog.save()
            return redirect(request.path, id=bag.id)

def tablocheckin(request, id):
    now = timezone.now()
    check = get_object_or_404(Checkin, id=id)
    if check.checkinfly is None:
        return render(request,'flightinfosystem/tablocheckinempty.html',{'check':check})
    else:
        flight = check.checkinfly
        return render(request, 'flightinfosystem/tablocheckinfly.html',
                      {'flight': flight, 'check': check})

def tablodeparture(request, past=11, future=24):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    departflights = Flight.objects.filter(ad=0).filter(timeplan__lt=futuretime). \
        filter(timeplan__gt=pasttime).order_by('timeplan')
    return render(request, 'flightinfosystem/tablodeparture.html',
           {'flights': departflights})