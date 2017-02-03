import datetime as DT
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

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

    #Вылетающий ли рейс
    def isdeparture(self):
        if self.ad == 0:
            return True
        else:
            return False
    #Прилитающий ли рейс
    def isarrivals(self):
        if self.ad == 1:
            return True
        else:
            return False

    # Рейс в аэропорту? Установлено время фактического события?
    def istimefact(self):
        if self.timefact is None:
            return False
        else:
            return True
    #Получить время начала регистрации
    def timestartcheckin(self, delta=180*60):
        return (self.timeplan - DT.timedelta(seconds=delta))
    #Получить время окончания регистрации
    def timestopcheckin(self, delta=40*60):
        return (self.timeexp - DT.timedelta(seconds=delta))
    #Получить время начала посадки
    def timestartboard(self, delta=20*60):
        return (self.timeexp - DT.timedelta(seconds=delta))
    #Получить время окончания посадки
    def timestopboard(self, delta=5*60):
        return (self.timeexp - DT.timedelta(seconds=delta))
    #Получить время начала выдачи багажа
    def timestartbaggege(self, delta=15 * 60):
        if self.istimefact():
            return self.timefact + DT.timedelta(seconds=delta)
        else:
            return self.timeexp + DT.timedelta(seconds=delta)
    #Получить время завершения выдачи багажа
    def timestopbaggege(self, delta=35 * 60):
        if self.timefact:
            return self.timefact + DT.timedelta(seconds=delta)
        else:
            return self.timeexp + DT.timedelta(seconds=delta)
    #Закрыта ли регистрация
    def ischeckinclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return flightstatus.checkin and flightstatus.checkinstop
    #Посадка началась
    def isboardopen(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return not flightstatus.boardstop and flightstatus.board
    #Посадка закрыта
    def isboardclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return flightstatus.board and flightstatus.boardstop
    #Выдача багажа начата
    def isbaggageopen(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return not flightstatus.baggagestop and flightstatus.baggage
    #Выдача багажа завершена
    def isbaggageclose(self):
        flightstatus = FlightStatus.objects.get(fly=self)
        return flightstatus.baggagestop and flightstatus.baggage

    #Рейс считается закрытым если: для прилетающего рейса завершилась выдача багажа, или прошло
    #достаточно времени с момент прилета. Для вылетающего рейса - если вылетел.
    def isclose(self):
        if self.isarrivals():
            if self.isbaggageclose():
                return True
            else:
                now = timezone.now()
                if now > self.timestartbaggege():
                        return True
                return False
        else:
            if self.istimefact():
                return True
            else:
                return False

    #Текстовый статус выдачи багажа (статусы для диспетчеров)
    def statebaggage(self):
        txt = 'baggabe Ошибка.'
        if not self.istimefact():
            txt = 'Рейс ожидается.'
        else:
            if self.isbaggageclose():
                txt = 'Багаж выдан. Рейс закрыт.'
            elif self.isbaggageopen():
                txt = 'Выдача багажа.'
            else:
                flightstatus = FlightStatus.objects.get(fly=self)
                now = timezone.now()
                if not flightstatus.baggage and not flightstatus.baggagestop:
                    if now <= self.timestartbaggege():
                        txt = 'Ожидается выдача багажа.'
                    else:
                        txt = 'Нарушение графика выдачи багажа!'
        return txt

    # Текстовый статус регистрации (статусы для диспетчеров)
    def statecheckin(self):
        txt = 'checkin Ошибка.'
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        if self.istimefact() or (flightstatus.checkin and flightstatus.checkinstop):
            txt = 'Регистрация закрыта.'
        else:
            if flightstatus.checkin and not flightstatus.checkinstop:
                txt = 'Регистрация открыта.'
            elif now > self.timestartcheckin() and not flightstatus.checkin:
                txt = 'Нарушение графика регистрации!'
            elif now <= self.timestartcheckin() and not flightstatus.checkin and not flightstatus.checkinstop:
                txt = 'Ожидается.'
        return  txt

    # Текстовый статус посадки (статусы для диспетчеров)
    def stateboard(self):
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        txt = 'board Ошибка.'
        if self.istimefact() or (flightstatus.board and flightstatus.boardstop):
            txt = 'Посадка завершена.'
        elif flightstatus.board and not flightstatus.boardstop:
            txt = 'Посадка пассажиров.'
        elif now > self.timestartboard() and not flightstatus.board:
            txt = 'Нарушение графика посадки!'
        elif self.timestopcheckin() < now <= self.timestartboard() and not flightstatus.board:
            txt = 'Ожидается посадка.'
        return txt

    # Текстовый статус рейса (статусы для диспетчеров)
    def stateflight(self):
        txt = 'Ошибка.'
        now = timezone.now()
        flightstatus = FlightStatus.objects.get(fly=self)
        #eventlogs = EventLog.objects.filter(fly=self)
        if self.isarrivals():
            if self.istimefact():
                txt = self.statebaggage()
        if self.isdeparture():
            txt = self.statecheckin() + ' ' + self.stateboard()
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
    #Статусы для вылетающего рейса
    checkin = models.BooleanField("Регистрация пассажиров", default=False)
    checkinstop = models.BooleanField("Конец регистрации", default=False)
    board = models.BooleanField("Статус посадки пассажиров", default=False)
    boardstop = models.BooleanField("Конец посадки пассажиров", default=False)
    #Статусы для прилетающего рейса
    baggage = models.BooleanField("Выдача багажа", default=False)
    baggagestop = models.BooleanField("Конец выдачи багажа", default=False)
    #Отработка ситуации замены борта
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

    def __str__(self):
        return self.fullname + ' ' + str(self.num)

    def open(self, fly):
        self.boardfly = fly
        now = timezone.now()
        self.starttime = now
        self.endtime = fly.timeexp - DT.timedelta(seconds=7 * 60)
        self.save()

    def close(self):
        self.boardfly = None
        self.starttime = None
        self.endtime = None
        self.save()

class Baggege(models.Model):
    baggagefly = models.ForeignKey('Flight', verbose_name="Рейс", blank=True, null=True, on_delete=models.SET_NULL)
    num = models.CharField("Номер карусели", max_length=2)
    shortname = models.CharField("Тип рейса", max_length=5)
    fullname = models.CharField("Терминал", max_length=13)
    starttime = models.DateTimeField("Начало выдачи", null=True, blank=True)
    endtime = models.DateTimeField("Конец выдачи", null=True, blank=True)

    def __str__(self):
        return self.shortname + ' ' + str(self.num)

    def open(self, fly):
        self.baggagefly = fly
        now = timezone.now()
        self.starttime = now
        self.endtime = now + DT.timedelta(seconds=20*60)
        self.save()

    def close(self):
        self.baggagefly = None
        self.starttime = None
        self.endtime = None
        self.save()

class AirlineManager(models.Manager):
    def getsmallogodict(self, flights):
        dic = {}
        now = timezone.now()
        codshares = Codeshare.objects.filter(startdate__lt=now).filter(stopdate__gt=now)
        for flight in flights:
            cod = flight.fly.split('-')[0]
            try:
                airline = Airline.objects.get(Q(cod_iata=cod) | Q(cod_icao=cod) | Q(cod_rus=cod))
            except ObjectDoesNotExist:
                dic[flight.fly] = ''
            except MultipleObjectsReturned:
                dic[flight.fly] = ''
            else:
                dic[flight.fly] = airline.smallogo.url
            if flight.iscodshare():
                for codshar in codshares:
                    if flight.fly == codshar.baseairline:
                        cod = codshar.shareairline.split('-')[0]
                        try:
                            airline = Airline.objects.get(cod_rus=cod)
                        except ObjectDoesNotExist:
                            dic[codshar.shareairline] = ''
                        except MultipleObjectsReturned:
                            dic[codshar.shareairline] = ''
                        else:
                            dic[codshar.shareairline] = airline.smallogo.url
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



