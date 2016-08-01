import datetime as DT
from django.utils import timezone
from django.db import models


# Create your models here.

class Flight(models.Model):
    fly = models.CharField("Рейс", max_length=9)
    ad = models.IntegerField("Направление")
    punktdist = models.CharField("Маршрут", max_length=100, blank=True)
    portdist = models.CharField("Аэропорты по маршруту", max_length=100, blank=True)
    aircraft = models.CharField("Тип ВС", max_length=10)
    carrname = models.CharField("Перевозчик", max_length=35)
    status = models.CharField("Статус рейса из AODB", max_length=60, blank=True)
    timeplan = models.DateTimeField("Время по плану", null=True, blank=True)
    timeexp = models.DateTimeField("Время расчетное", null=True, blank=True)
    timefact = models.DateTimeField("Время по факту", null=True, blank=True)

    def __str__(self):
        localtime = timezone.localtime(self.timeplan)
        if self.ad == 1:
            ad = 'прилетающий'
        else:
            ad = 'вылетающий'
        return ad + ' рейс ' + self.fly + ' за ' + localtime.strftime('%d.%m.%y')

    def isdeparture(self):
        if self.ad == 0:
            return True
        else:
            return False

    def isarrivals(self):
        if self.ad == 1:
            return True
        else:
            return False

    def timestartcheckin(self, delta=120*60):
        return (self.timeexp - DT.timedelta(seconds=delta))

    def timestopcheckin(self, delta=40*60):
        return (self.timeexp - DT.timedelta(seconds=delta))

    def timestartboard(self, delta=20*60):
        return (self.timeexp - DT.timedelta(seconds=delta))

    def timestopboard(self, delta=5*60):
        return (self.timeexp - DT.timedelta(seconds=delta))

    def stateflight(self):
        txt = self.status
        flightstatus = FlightStatus.objects.get(fly=self)
        if self.isarrivals():
            if flightstatus.baggage:
                txt = txt + ' Выдача багажа'
            if flightstatus.baggagestop:
                txt = txt + ' Багаж выдан'
        if self.isdeparture():
            if flightstatus.checkin:
                txt = txt + 'Регистрация открыта'
            if flightstatus.checkinstop:
                txt = txt + 'Регистрация закрыта'
            if flightstatus.board:
                txt = txt + 'Посадка пассажиров'
            if flightstatus.boardstop:
                txt = txt + 'Посадка закрыта'
        return txt

    def isclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        if self.isarrivals():
            if flightstatus.baggagestop:
                return True
            else:
                return False
        else:
            if self.timefact is not None:
                return True
            else:
                return False


class FlightStatus(models.Model):
    fly = models.OneToOneField('Flight', verbose_name="Рейс")
    checkin = models.BooleanField("Регистрация пассажиров", default=False)
    checkinstop = models.BooleanField("Конец регистрации", default=False)
    board = models.BooleanField("Статус посадки пассажиров", default=False)
    boardstop = models.BooleanField("Конец посадки пассажиров", default=False)
    baggage = models.BooleanField("Выдача багажа", default=False)
    baggagestop = models.BooleanField("Конец выдачи багажа", default=False)
    changeboard = models.BooleanField("Статус замены борта", default=False)

class Event(models.Model):
    name = models.CharField("Имя события", max_length=15)

class EventLog(models.Model):
    fly = models.ForeignKey('Flight', verbose_name="Рейс", )
    event = models.ForeignKey('Event', verbose_name="Событие")
    descript = models.CharField("Допопции события", max_length=60)
    timestamp = models.DateTimeField("Время события", auto_now=True)

    def geteventname(self):
        return self.event.name

class Checkin(models.Model):
    num = models.CharField("Номер стойки", max_length=2)
    fullname = models.CharField("Имя терминала", max_length=21)
    shortname = models.CharField("Короткое имя стойки", max_length=5)
    checkinfly = models.ForeignKey('Flight', verbose_name='Рейс', blank=True, null=True, on_delete=models.SET_NULL)
    classcheckin = models.CharField("Класс обслуживания", max_length=15, blank=True, null=True)
    deltastartcheckin = models.IntegerField("Начало регистрации", default=7200)
    deltastopcheckin = models.IntegerField("Конец регистрации", default=2400)
    def __str__(self):
        return 'Стойка регистрации ' + self.shortname + ' ' + str(self.num)

class Board(models.Model):
    boardfly = models.ForeignKey('Flight', verbose_name="Рейс", blank=True, null=True, on_delete=models.SET_NULL)
    num = models.CharField("Номер выхода", max_length=2)
    fullname = models.CharField("Имя терминала", max_length=21)
    shortname = models.CharField("Имя выхода", max_length=8)
'''
class BaggegeFlightStatus(models.Model):
    fly = models.ForeignKey('Flights', verbose_name="Рейс")
    starchecktime = models.TimeField("Начало выдачи", null=True)
    endchecktime = models.TimeField("Конец выдачи", null=True)
    checkins = models.CharField("Используемая карусель", max_length=13, blank=True) '''