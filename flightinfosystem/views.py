from django.shortcuts import render, get_object_or_404
from .models import FlightsStatus, Flights, Checkin

# Create your views here.
def flight_list(request):
    flights = Flights.objects.all().order_by('timeplan')
    return render(request,'flightinfosystem/flight_list.html',{'flights': flights})

def flight_detail(request, id):
    flight = get_object_or_404(Flights, id=id)
    return render(request,'flightinfosystem/flight_detail.html',{'flight': flight})

def checkin_list(request):
    checkins = Checkin.objects.all()
    return render(request, 'flightinfosystem/checkin_list.html', {'checkins': checkins})

def check(request, id):
    checkin = get_object_or_404(Checkin, id=id)
    return render(request,'flightinfosystem/checkin1.html',{'checkin': checkin})
