import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import pytz

from .models import Flight, Checkin, FlightStatus, EventLog


# Create your views here.
def index(request):
    return render(request, 'flightinfosystem/index.html', {})


def flight_list(request, past=11, future=11):
    now = timezone.now()
    pasttime = now - datetime.timedelta(seconds=past * 3600)
    futuretime = now + datetime.timedelta(seconds=future * 3600)
    flights = Flight.objects.filter(timeplan__lt=futuretime).filter(timeplan__gt=pasttime).order_by('timeplan')
    return render(request, 'flightinfosystem/flight_list.html', {'flights': flights})

def flight_detail(request, id):
    flight = get_object_or_404(Flight, id=id)
    flightstatus = FlightStatus.objects.get(fly=flight)

    return render(request, 'flightinfosystem/flight_detail.html', {'flight': flight,
                                                                   'flightstatus': flightstatus})

def checkin_list(request):
    checkins = Checkin.objects.all()
    return render(request, 'flightinfosystem/checkin_list.html', {'checkins': checkins})


def checkin(request, id, past=11, future=11):
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
            check.startcheckin = selectflight.timestartcheckin()
            check.stopcheckin = selectflight.timestopcheckin()
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
                flightstatus.checkin = False
                flightstatus.checkinstop = True
                flightstatus.save()
                text = check.shortname + ' ' + check.num
                eventlog = EventLog(fly=fly, event_id=6, descript=text)
                eventlog.save()
                eventlog = EventLog(fly=fly, event_id=7, descript='')
                eventlog.save()
            else:
                eventlog = EventLog(fly=fly, event_id=6, descript=text)
                eventlog.save()
            return redirect(request.path, id=check.id)

def tablocheckin(request, id):
    timezone.activate(pytz.timezone('Asia/Irkutsk'))
    now = timezone.now()
    check = get_object_or_404(Checkin, id=id)
    if check.checkinfly is None:
        return HttpResponse('Нет регистрации')
    else:
        flight = check.checkinfly
        return render(request, 'flightinfosystem/tablocheckin.html',
                      {'flight': flight, 'check': check, 'now': now})

def tsttablocheckin(request, id):
    check = get_object_or_404(Checkin, id=id)
    if check.checkinfly is None:
        return HttpResponse('Нет регистрации')
    else:
        flight = check.checkinfly
        starttime = flight.timeexp - datetime.timedelta(seconds=7200)
        stoptime = flight.timeexp - datetime.timedelta(seconds=2400)
        return render(request, 'flightinfosystem/tablotst.html',
                      {'flight': flight, 'check': check, 'start': starttime, 'stop': stoptime})