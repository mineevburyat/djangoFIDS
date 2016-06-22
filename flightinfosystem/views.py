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
    departureflight = Flights.objects.filter(ad=0)
    return render(request,'flightinfosystem/checkin.html',{'check': check})
    #return HttpResponse('This is checkin number {} for airport Baikal'.format(id))
