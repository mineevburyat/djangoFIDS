from django.contrib import admin
from .models import Flight, FlightStatus, Checkin
# Register your models here.
admin.site.register((Flight, FlightStatus, Checkin))