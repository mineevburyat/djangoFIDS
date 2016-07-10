from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
import datetime
from .models import Event, EventLog, Flight, FlightStatus, Checkin


# Create your views here.
def index(request):
    return HttpResponse('This is flight information system for airport Baikal')

def flight_list(request):
    flights = Flight.objects.all().order_by('timeplan')
    return render(request,'flightinfosystem/flight_list.html',{'flights': flights})

def flight_detail(request, id):
    flight = get_object_or_404(Flight, id=id)
    return render(request,'flightinfosystem/flight_detail.html',{'flight': flight})

def checkin_list(request):
    checkins = Checkin.objects.all()
    return render(request, 'flightinfosystem/checkin_list.html', {'checkins': checkins})

def checkin(request, id):
    check = get_object_or_404(Checkin, id=id)
    if request.method == 'GET':
        if check.checkinfly_id is None:
            #Отобразить рейсы 3 часа вперед и три часа назад от текущего времени,
            # возможность выбора рейса
            departureflight = Flights.objects.filter(ad=0).order_by('timeplan')
            return render(request, 'flightinfosystem/checkin-select.html', {'check': check,
                                                                 'depart': departureflight})
        else:
            #Отобразить статусы рейса прикрепленного к стойке и возможность закрыть регистрацию на стойке
            flystatuscheckin = check.checkinfly
            flight = flystatuscheckin.fly
            checkinswithflystat = Checkin.objects.filter(checkinfly_id=flystatuscheckin.id)
            txt = ''
            for num in checkinswithflystat:
                txt += ' '+ str(num.shortname) + ' ' + str(num.num)
            return render(request, 'flightinfosystem/checkin-status.html',
                          {'check': check, 'flight': flight, 'statuscheck':flystatuscheckin, 'checkins': txt})
    elif request.method == 'POST':
        if check.checkinfly is None:
            # Внести данные в flightinfo и переслать на страницу статуса рейса превязанного к стойке
            flightid = request.POST['id']
            selectflight = get_object_or_404(Flights, id=flightid)
            try:
                flightstatus = FlightsStatus.objects.get(fly_id=flightid)
            except FlightsStatus.DoesNotExist:
                flightstatus = FlightsStatus(statuscheckin=True, fly_id=selectflight.id)
                flightstatus.save()
            try:
                checkinflight = CheckinFlightStatus.objects.get(fly_id=flightid)
            except CheckinFlightStatus.DoesNotExist:
                txt = "cтойка: " + check.shortname + ' ' + str(check.num)
                checkinflight = CheckinFlightStatus(fly_id=selectflight.id, starchecktime=datetime.datetime.now(),
                                                endchecktime=selectflight.timestopcheckin(),
                                                checkins=txt)
                checkinflight.save()
            else:
                txt = checkinflight.checkins
                checkinflight.checkins = txt + ', ' + str(check.num)
                checkinflight.save()
            check.checkinfly_id = checkinflight.id
            check.classcheckin = request.POST['class']
            check.save()
            return redirect('flightinfosystem.views.checkin', id=check.id)
        else:
            # внести данные о времени начала регитсрации и названия номера стойки, либо отмена привязки
            checkinflystat = check.checkinfly

            return HttpResponse('Внесение изменений в ')

