import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

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
            startcheckin = []
            stopcheckin = []
            for depart in departureflight:
                startcheckin.append(depart.timestartcheckin(delta=check.deltastartcheckin))
                stopcheckin.append(depart.timestopcheckin(delta=check.deltastopcheckin))
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
        if check.checkinfly is None:
            # Внести данные в flightstat и eventlog и переслать на страницу статуса рейса превязанного к стойке
            flightid = request.POST['id']
            selectflight = get_object_or_404(Flight, id=flightid)
            flightstatus = FlightStatus.objects.get(fly=selectflight)
            if not flightstatus.checkin:
                flightstatus.checkin = True
                flightstatus.save()
                text = 'стойка ' + check.shortname + ' ' + check.num
                eventlog = EventLog(fly=selectflight, event_id=4, descript=text)
                eventlog.save()
            else:
                text = 'стойка ' + check.shortname + ' ' + check.num
                eventlog = EventLog(fly=selectflight, event_id=5, descript=text)
                eventlog.save()
            check.checkinfly = selectflight
            check.classcheckin = request.POST['class']
            check.save()
            return redirect('/fids/checkin/', id=check.id)
        else:
            # внести данные о времени начала регитсрации и названия номера стойки, либо отмена привязки
            checkinflystat = check.checkinfly

            return HttpResponse('Внесение изменений в ')

