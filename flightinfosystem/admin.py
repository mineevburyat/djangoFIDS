from django.contrib import admin
from .models import Flights, FlightsStatus, Checkin
# Register your models here.
admin.site.register((Flights, FlightsStatus, Checkin))