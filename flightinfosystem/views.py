from django.shortcuts import render
from .models import FlightsStatus, Flights

# Create your views here.
def flight_list(request):
    flights = Flights.objects.all()
    return render(request,'flightinfosystem/flight_list.html',{'flights': flights})