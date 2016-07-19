import datetime as DT

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
        if self.ad == 1:
            ad = 'прилетающий'
        else:
            ad = 'вылетающий'
        return ad + ' рейс: ' + self.fly + ' на ' + self.timeplan.strftime('%d.%m.%y %H:%M')

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

    def timestartcheckin(self, delta=7200):
        return (self.timeexp - DT.timedelta(seconds=delta))

    def timestopcheckin(self, delta=2400):
        return (self.timeexp - DT.timedelta(seconds=delta))

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

class Checkin(models.Model):
    num = models.CharField("Номер стойки", max_length=2)
    fullname = models.CharField("Полное имя стойки", max_length=21)
    shortname = models.CharField("Короткое имя стойки", max_length=5)
    checkinfly = models.ForeignKey('Flight', verbose_name='Рейс', blank=True, null=True, on_delete=models.SET_NULL)
    classcheckin = models.CharField("Класс обслуживания", max_length=15, blank=True, null=True)
    deltastartcheckin = models.IntegerField("Начало регистрации", default=7200)
    deltastopcheckin = models.IntegerField("Конец регистрации", default=2400)
    def __str__(self):
        return 'Стойка регистрации ' + self.shortname + ' ' + str(self.num)

'''class BoardFlightStatus(models.Model):
    fly = models.ForeignKey('Flights', verbose_name="Рейс")
    starchecktime = models.TimeField("Начало посадки", null=True)
    endchecktime = models.TimeField("Конец посадки", null=True)
    checkins = models.CharField("Используемый выход", max_length=13, blank=True)

class BaggegeFlightStatus(models.Model):
    fly = models.ForeignKey('Flights', verbose_name="Рейс")
    starchecktime = models.TimeField("Начало выдачи", null=True)
    endchecktime = models.TimeField("Конец выдачи", null=True)
    checkins = models.CharField("Используемая карусель", max_length=13, blank=True) '''