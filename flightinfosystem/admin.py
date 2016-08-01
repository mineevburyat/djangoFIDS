from django.contrib import admin
from .models import Flight, FlightStatus, Checkin, Event, EventLog, Board
# Register your models here.

@admin.register(Flight)
class AdminFlight(admin.ModelAdmin):
    list_display = []

@admin.register(Checkin)
class AdminCheckin(admin.ModelAdmin):
    list_display = ['num', 'fullname', 'shortname', 'checkinfly']
    ordering = ['fullname', 'num']

@admin.register(Board)
class AdminBoard(admin.ModelAdmin):
    list_display = ['num', 'fullname', 'shortname', 'boardfly']
    ordering = ['fullname', 'num']


@admin.register(FlightStatus)
class AdminFlightStatus(admin.ModelAdmin):
    pass

@admin.register(Event)
class AdminEvent(admin.ModelAdmin):
    pass

@admin.register(EventLog)
class AdminEventLog(admin.ModelAdmin):
    pass