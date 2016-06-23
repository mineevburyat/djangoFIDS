from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import FlightsStatus, Flights, Checkin


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
    if check.flightstatus is None:
        #Отобразить рейсы 3 часа вперед и три часа назад от текущего времени,
        # возможность выбора рейса
        departureflight = Flights.objects.filter(ad=0).order_by('timeplan')
        return render(request, 'flightinfosystem/checkin-select.html', {'check': check,
                                                                 'depart': departureflight})
    else:
        #Отобразить статусы рейса прикрепленного к стойке и возможность закрыть регистрацию на стойке
        pass
    departureflight = Flights.objects.filter(ad=0)
    flightstatus = FlightsStatus.objects.all()
    return render(request,'flightinfosystem/checkin.html',{'check': check,
                                                           'depart': departureflight,
                                                           'status': flightstatus})
    #return HttpResponse('This is checkin number {} for airport Baikal'.format(id))
