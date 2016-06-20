from django.db import models
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
        return 'рейс: ' + self.fly + ' на ' + self.timeplan.strftime('%d.%m.%y %H:%M')

class FlightsStatus(models.Model):
    fly = models.ForeignKey('Flights', verbose_name="Рейс")
    statuscheckin = models.BooleanField("Статус регистрации пассажиров", default=False)
    statusboard = models.BooleanField("Статус посадки пассажиров", default=False)
    statusbaggage = models.BooleanField("Статус выдачи багажа", default=False)
    checkins = models.CharField("Используемые стойки регистрации", max_length=13, blank=True)
    gate = models.CharField("Используемый выход для посадки", max_length=4, blank=True)
    baggage = models.CharField("Используемая лента выдачи багажа", max_length=4, blank=True)

    def __str__(self):
        return str(self.fly)