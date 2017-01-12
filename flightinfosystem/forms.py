from django import forms

from .models import Flight, FlightStatus, Baggege, Board



class FlightStatusDepartForm(forms.ModelForm):
    class Meta:
        model = FlightStatus
        fields = ['fly','checkin', 'checkinstop', 'board', 'boardstop']

class FlightStatusArrivalFormBaggageOpen(forms.ModelForm):
    class Meta:
        model = Baggege
        fields = ['num']

class FlightStatusArrivalFormBaggageClose(forms.ModelForm):
    class Meta:
        model = FlightStatus
        fields = ['fly', 'baggage', 'baggagestop']

#Форма для открытия выдачи багажа (просто выбрать номер карусели), по событию определяется время и
#ставится флаг соответсвующего статуса
class ArriavalBaggageOpen(forms.Form):
    carusel = forms.ModelChoiceField(queryset=Baggege.objects.all(),
                                     label="Выберите багажную карусель:")
    baggageopen = forms.BooleanField(initial=True, widget=forms.HiddenInput)

    #def is_valid(self):

#Форма для закрытия выдачи багажа (просто согласиться с закрытием), по событию определяется время и
#ставится флаг соответсвующего статуса
class ArriavalBaggageClose(forms.Form):
    baggageclose = forms.BooleanField(initial=True, widget=forms.HiddenInput)

#Форма для открытия посадки пассажиров (просто выбрать номер выхода), по событию определяется время и
#ставится флаг соответсвующего статуса
class DepartureBoardOpen(forms.Form):
    gate = forms.ModelChoiceField(queryset=Board.objects.all(),
                                     label="Выберите выход:")
    boardopen = forms.BooleanField(initial=True, widget=forms.HiddenInput)

#Форма для закрытия посадки пассажиров, по событию определяется время и
#ставится флаг соответсвующего статуса
class DepartureBoardClose(forms.Form):
    boardclose = forms.BooleanField(initial=True, widget=forms.HiddenInput)