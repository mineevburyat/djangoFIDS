from django import forms

from .models import Flight, FlightStatus



class FlightStatusDepartForm(forms.ModelForm):
    class Meta:
        model = FlightStatus
        fields = ['fly','checkin', 'checkinstop', 'board', 'boardstop']

class FlightStatusArrivalForm(forms.ModelForm):
    class Meta:
        model = FlightStatus
        fields = ['fly', 'baggage', 'baggagestop']
