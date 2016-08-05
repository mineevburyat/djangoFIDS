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

    def timestartbaggege(self, delta=15 * 60):
        if not self.timefact:
            return self.timeexp + DT.timedelta(seconds=delta)
        else:
            return self.timefact + DT.timedelta(seconds=delta)

    def timestopbaggege(self, delta=30 * 60):
        return (self.timeexp + DT.timedelta(seconds=delta))

    def ischeckinclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return flightstatus.checkinstop

    def isboardclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return not flightstatus.board and flightstatus.boardstop

    def isbaggageclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return flightstatus.baggagestop

    def istimefact(self):
        if self.timefact is not None:
            return True
        else:
            return False

    def isclose(self):
        delta = 120
        flightstatus = FlightStatus.objects.get(fly=self)
        if self.isarrivals():
            if flightstatus.baggagestop:
                return True
            else:
                now = timezone.now()
                tdelta = DT.timedelta(seconds=delta * 60)
                if self.istimefact():
                    if now > self.timefact + tdelta:
                        return True
                return False
        else:
            if self.istimefact():
                return True
            else:
                return False

    def statebaggage(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        txt = 'Ошибка'
        if self.isarrivals():
            if self.istimefact():
                if not flightstatus.baggage:
                    if not flightstatus.baggagestop:
                        txt = 'Не начиналось'
                    else:
                        txt = 'Выдан'
                else:
                    if not flightstatus.baggagestop:
                        txt = 'Выдача'
                    else:
                        txt = 'Выдан'
            else:
                txt = 'Ожидается'
        return txt

    def statecheckin(self):
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        txt = 'Ошибка'
        if self.isdeparture():
            if self.istimefact() and not flightstatus.checkin and not flightstatus.checkinstop:
                txt = 'Не надо. Вылетел'
            elif flightstatus.checkin and not flightstatus.checkinstop:
                txt = 'Открыта'
            elif flightstatus.checkin and flightstatus.checkinstop:
                txt = 'Закрыта'
            elif now > self.timestartcheckin() and not flightstatus.checkin:
                txt = 'Нарушение графика'
            elif not self.istimefact() and not flightstatus.checkin and not flightstatus.checkinstop:
                txt = 'Не начиналось'
        return  txt


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
    startcheckin = models.DateTimeField("Начало регистрации", blank=True, null=True)
    stopcheckin = models.DateTimeField("Конец регистрации", blank=True, null=True)
    def __str__(self):
        return 'Стойка регистрации ' + self.shortname + ' ' + str(self.num)

class Board(models.Model):
    boardfly = models.ForeignKey('Flight', verbose_name="Рейс", blank=True, null=True, on_delete=models.SET_NULL)
    num = models.CharField("Номер выхода", max_length=2)
    fullname = models.CharField("Имя терминала", max_length=21)
    shortname = models.CharField("Имя выхода", max_length=8)
    starttime = models.DateTimeField("Начало посадки", null=True, blank=True)
    endtime = models.DateTimeField("Конец посадки", null=True, blank=True)

class Baggege(models.Model):
    baggagefly = models.ForeignKey('Flight', verbose_name="Рейс", blank=True, null=True, on_delete=models.SET_NULL)
    num = models.CharField("Номер карусели", max_length=2)
    shortname = models.CharField("Тип рейса", max_length=5)
    fullname = models.CharField("Терминал", max_length=13)
    starttime = models.DateTimeField("Начало выдачи", null=True, blank=True)
    endtime = models.DateTimeField("Конец выдачи", null=True, blank=True)
