import datetime as DT
from django.utils import timezone
from django.db import models
from django.db.models import Q


# Create your models here.
class Codeshare(models.Model):
    baseairline = models.CharField("Основной рейс", max_length=8)
    shareairline = models.CharField("Совмещенный рейс", max_length=8)
    startdate = models.DateTimeField("Начало действия", default=timezone.now())
    stopdate = models.DateTimeField("Окончание действия", default=timezone.now() + DT.timedelta(days=3650))
    description = models.TextField("Описание документа о совместном рейсе", null=True, blank=True)

    def __str__(self):
        today = timezone.now()
        if self.startdate <= today <= self.stopdate:
            txt = " действует"
        else:
            txt = " закончилось"
        return 'Совмещенные рейсы ' + self.baseairline + ' - ' + self.shareairline + txt

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
        delta = 60
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

    def stateboard(self):
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        txt = 'Ошибка'
        if self.isdeparture():
            if self.istimefact() and not flightstatus.board and not flightstatus.boardstop:
                txt = 'Не надо. Вылетел'
            elif flightstatus.board and not flightstatus.boardstop:
                txt = 'Посадка'
            elif flightstatus.board and flightstatus.boardstop:
                txt = 'Посадка закрыта'
            elif now > self.timestartboard() and not flightstatus.board:
                txt = 'Нарушение графика'
            elif not self.istimefact() and not flightstatus.board and not flightstatus.boardstop:
                txt = 'Не начиналось'
        return txt

    def stateflight(self):
        txt = 'Ошибка'
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        eventlogs = EventLog.objects.filter(fly=self)
        if self.isarrivals():
            if self.istimefact():
                if now < self.timestartbaggege() and not flightstatus.baggage and not flightstatus.baggagestop:
                    txt = 'Ожидается выдача багажа'
                elif now > self.timestartbaggege() and not flightstatus.baggage and not flightstatus.baggagestop:
                    txt = 'Нарушение графика выдачи багажа'
                if flightstatus.baggage and not flightstatus.baggagestop:
                    txt = 'Выдача багажа'
                elif flightstatus.baggage and flightstatus.baggagestop:
                    txt = 'Багаж выдан'
            else:
                txt = 'Ожидается'
        if self.isdeparture():
            if self.isclose():
                if flightstatus.boardstop:
                    boardstarttime = timezone.localtime(eventlogs.filter(event_id=9)[0].timestamp)
                    txt = 'Вылетел. Посадка закрыта в ' + boardstarttime.strftime('%H:%M')
                else:
                    txt = "Вылетел."
            else:
                if now > self.timestartcheckin() and not flightstatus.checkin and not flightstatus.checkinstop and not flightstatus.board and not flightstatus.boardstop:
                    txt = 'Нарушение графика обслуживания'
                elif now < self.timestartcheckin() and not flightstatus.checkin and not flightstatus.checkinstop and not flightstatus.board and not flightstatus.boardstop:
                    txt = 'Ожидается'
                elif flightstatus.checkin and not flightstatus.checkinstop and not flightstatus.board and not flightstatus.boardstop:
                    checkinstarttime = timezone.localtime(eventlogs.filter(event_id=4)[0].timestamp)
                    txt = 'Регистрация открылась в ' + checkinstarttime.strftime('%H:%M')
                elif flightstatus.checkin and flightstatus.checkinstop and not flightstatus.board and not flightstatus.boardstop:
                    checkinstoptime = timezone.localtime(eventlogs.filter(event_id=7)[0].timestamp)
                    txt = 'Регистрация закрыта  в ' + checkinstoptime.strftime('%H:%M')
                elif flightstatus.checkin and flightstatus.checkinstop and flightstatus.board and not flightstatus.boardstop:
                    boardname = eventlogs.filter(event_id=8)[0].descript
                    boardstarttime = timezone.localtime(eventlogs.filter(event_id=8)[0].timestamp)
                    txt = 'Посадка пассажиров. ' + boardname + ' в ' + boardstarttime.strftime('%H:%M')
                elif flightstatus.checkin and flightstatus.checkinstop and flightstatus.board and flightstatus.boardstop:
                    boardstarttime = timezone.localtime(eventlogs.filter(event_id=9)[0].timestamp)
                    txt = 'Посадка закрыта в ' + boardstarttime.strftime('%H:%M')
        return txt

    #Есть ли совмещенные рейсы
    def iscodshare(self):
        now = timezone.now()
        codshare = Codeshare.objects.filter(startdate__lt=now).filter(stopdate__gt=now).filter(baseairline=self.fly)
        if len(codshare) == 0:
            return False
        else:
            return True

    #Выдать список совмещенных рейсов
    def listcodshare(self):
        now = timezone.now()
        codshares = Codeshare.objects.filter(startdate__lt=now).filter(stopdate__gt=now).filter(baseairline=self.fly)
        lst = []
        for codshar in codshares:
            lst.append(codshar.shareairline)
        return lst

    #Выдать url на большой логотип авиакомпании
    def getbiglogo(self):
        cod = self.fly.split('-')[0]
        airline = Airline.objects.get(Q(cod_iata=cod) | Q(cod_icao=cod) | Q(cod_rus=cod))
        return airline.biglogo.url

    # Выдать url на маленький логотип авиакомпании
    def getsmalogo(self):
        cod = self.fly.split('-')[0]
        airline = Airline.objects.get(Q(cod_iata=cod) | Q(cod_icao=cod) | Q(cod_rus=cod))
        return airline.smallogo.url


class FlightStatus(models.Model):
    fly = models.OneToOneField('Flight', verbose_name="Рейс")
    checkin = models.BooleanField("Регистрация пассажиров", default=False)
    checkinstop = models.BooleanField("Конец регистрации", default=False)
    board = models.BooleanField("Статус посадки пассажиров", default=False)
    boardstop = models.BooleanField("Конец посадки пассажиров", default=False)
    baggage = models.BooleanField("Выдача багажа", default=False)
    baggagestop = models.BooleanField("Конец выдачи багажа", default=False)
    changeboard = models.BooleanField("Статус замены борта", default=False)

    def __str__(self):
        return 'id= ' + str(self.id) + ', ' + str(self.fly)

class Event(models.Model):
    name = models.CharField("Имя события", max_length=15)

    def __str__(self):
        return 'id= ' + str(self.id) + ', ' + str(self.name)

class EventLog(models.Model):
    fly = models.ForeignKey('Flight', verbose_name="Рейс", )
    event = models.ForeignKey('Event', verbose_name="Событие")
    descript = models.CharField("Допопции события", max_length=60)
    timestamp = models.DateTimeField("Время события", auto_now=True)

    def __str__(self):
        return 'id= ' + str(self.id) + ', ' + str(self.fly) + ', ' + str(self.event) + ', ' + str(self.descript)

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

class AirlineManager(models.Manager):
    def getsmallogodict(self, flights):
        dic = {}
        now = timezone.now()
        codshares = Codeshare.objects.filter(startdate__lt=now).filter(stopdate__gt=now)
        for flight in flights:
            cod = flight.fly.split('-')[0]
            airline = Airline.objects.get(Q(cod_iata=cod) | Q(cod_icao=cod) | Q(cod_rus=cod))
            dic[flight.fly] = airline.smallogo.url
            if flight.iscodshare():
                for codshar in codshares:
                    if flight.fly == codshar.baseairline:
                        cod = codshar.shareairline.split('-')[0]
                        airline = Airline.objects.filter(Q(cod_iata=cod) | Q(cod_icao=cod) | Q(cod_rus=cod))
                        if len(airline) == 0:
                            dic[codshar.shareairline] = cod
                        else:
                            dic[codshar.shareairline] = airline[0].smallogo.url
        return  dic

class Airline(models.Model):
    cod_iata = models.CharField("Код авиакомпании IATA", max_length=2, null=True)
    cod_icao = models.CharField("Код авиакомпании ICAO", max_length=3, null=True)
    cod_rus = models.CharField("Код авиакомпании внутренний", max_length=2, unique=True)
    name_ru = models.CharField("Полное наименование русское", max_length=25)
    name_en = models.CharField("Полное наименование междунар.", max_length=25)
    biglogo = models.ImageField("Большой логотип", upload_to='biglogo/')
    smallogo = models.ImageField("Малый логотип", upload_to='smallogo/')
    objects = AirlineManager()

    def __str__(self):
        return 'Авиакомпания ' + self.name_ru + '(' + self.cod_rus + ')'

    #выдать малый логотип по имени рейса
    #def getsmallurllogo(self, fly):
    #    cod = fly.split('-')[0]



