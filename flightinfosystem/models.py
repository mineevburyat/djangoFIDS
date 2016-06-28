from django.db import models
import datetime
#from django.utils import timezone
# Create your models here.

class Flights(models.Model):
    fly = models.CharField("Рейс", max_length=9)
    ad = models.IntegerField("Направление")
    punktdist = models.CharField("Маршрут", max_length=100, blank=True)
    portdist = models.CharField("Аэропорты", max_length=100, blank=True)
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

    def isarrive(self):
        if self.ad == 1:
            return True
        else:
            return False

    def timestartcheckin(self):
        return (self.timeexp - datetime.timedelta(seconds=7200)).time()

    def timestopcheckin(self):
        return (self.timeexp - datetime.timedelta(seconds=2400)).time()

class FlightsStatus(models.Model):
    fly = models.OneToOneField('Flights', verbose_name="Рейс")
    statuscheckin = models.BooleanField("Статус процесса регистрации", default=False)
    statusboard = models.BooleanField("Статус посадки пассажиров", default=False)
    statusbaggage = models.BooleanField("Статус выдачи багажа", default=False)

class CheckinFlightStatus(models.Model):
    fly = models.OneToOneField('Flights', verbose_name="Рейс", )
    starchecktime = models.TimeField("Начало регистрации", null=True)
    endchecktime = models.TimeField("Конец регистрации", null=True)
    checkins = models.CharField("Используемые стойки регистрации", max_length=13, blank=True)

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

class Checkin(models.Model):
    num = models.IntegerField("Номер стойки", editable=False)
    fullname = models.CharField("Полное имя стойки", max_length=21, editable=False)
    shortname = models.CharField("Короткое имя стойки", max_length=5, editable=False)
    checkinfly = models.ForeignKey('CheckinFlightStatus', verbose_name='Рейс', null=True, on_delete=models.SET_NULL)
    classcheckin = models.CharField("Классность", max_length=15, blank=True)
    def __str__(self):
        return 'Стойка регистрации ' + self.shortname + ' ' + str(self.num)