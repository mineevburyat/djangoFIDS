from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import CheckinFlightStatus, Flights, \
    FlightsStatus,BaggegeFlightStatus, BoardFlightStatus, Checkin


# Create your views here.
def index(request):
    return HttpResponse('This is flight information system for airport Baikal')

def flight_list(request):
    flights = Flights.objects.all().order_by('timeplan')
    return render(request,'flightinfosystem/flight_list.html',{'flights': flights})

def flight_detail(request, id):
    flight = get_object_or_404(Flights, id=id)
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
            idfly = check.checkinfly_id
            return render(request, 'flightinfosystem/checkin-status.html',
                          {'check': check, 'idfly': idfly})
    elif request.method == 'POST':
        if check.checkinfly is None:
            # Внести данные в flightinfo и переслать на страницу статуса рейса превязанного к стойке
            flightid = request.POST['id']
            selectflight = get_object_or_404(Flights, id=flightid)
            flightstatus = FlightsStatus()
            flightstatus.statuscheckin = True
            flightstatus.fly_id = selectflight.id
            flightstatus.save()
            checkinflight = CheckinFlightStatus()
            checkinflight.fly_id = selectflight.id
            checkinflight.starchecktime = timezone.now()
            checkinflight.endchecktime = selectflight.timeexp
            checkinflight.checkins = "cтойки: " + check.shortname + ' ' + str(check.num)
            checkinflight.save()
            check.checkinfly_id = selectflight.id
            check.classcheckin = request.POST['class']
            check.save()
            return redirect('flightinfosystem.views.checkin', id=check.id)
        else:
            # внести данные о времени начала регитсрации и названия номера стойки, либо отмена привязки
            return HttpResponse('Внесение изменений в ')

