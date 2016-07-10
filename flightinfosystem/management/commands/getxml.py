import sys
import os
import pytz
from xml.etree.ElementTree import parse
import datetime as DT
from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand, CommandError
from flightinfosystem.models import Flight

if int(sys.version_info[0]) == 3:
    from http.client import HTTPConnection
else:
    raise Exception("Version python less then 3")


class FlightsXML(list):
    def __init__(self):
        self = []

    def getfromxml(self, xmlfile):
        '''"Convert XML to Dict"'''
        flightinfo = {}
        tree = parse(xmlfile)
        for fly in tree.findall('FLY'):
            flycod = fly.attrib['number']
            if flycod is '':
                print(flycod, '-')
                continue
            flightinfo['fly'] = flycod
            airportdist = ''
            destinetion = ''
            for flightparam in fly.getchildren():
                if flightparam.tag.find('PORTDIST') != -1:
                    if flightparam.text is not None:
                        if airportdist == '':
                            airportdist = flightparam.text
                        else:
                            airportdist += ' - ' + flightparam.text
                    continue
                if flightparam.tag.find('PUNKTDIST') != -1:
                    if flightparam.text is not None:
                        if destinetion == '':
                            destinetion = flightparam.text
                        else:
                            destinetion += ' - ' + flightparam.text
                    continue
                flightinfo.setdefault(flightparam.tag, flightparam.text)
            flightinfo['portdist'] = airportdist
            flightinfo['punktdist'] = destinetion
            # перевести дату и время в удобный абсолютный формат (с часовым поясом)
            zone = 'Asia/Irkutsk'
            if flightinfo['TPLAN'] is None or flightinfo['DPLAN'] is None:
                flightinfo['timeplan'] = None
            else:
                naivet = DT.datetime.strptime(flightinfo['DPLAN'] + ' ' + flightinfo['TPLAN'], '%d.%m.%Y %H:%M')
                flightinfo['timeplan'] = pytz.timezone(zone).localize(naivet,is_dst=False)
            if flightinfo['TEXP'] is None or flightinfo['DEXP'] is None:
                flightinfo['timeexp'] = None
            else:
                naivet = DT.datetime.strptime(flightinfo['DEXP'] + ' ' + flightinfo['TEXP'], '%d.%m.%Y %H:%M')
                flightinfo['timeexp'] = pytz.timezone(zone).localize(naivet,is_dst=False)
            if flightinfo['TFACT'] is None or flightinfo['DFACT'] is None:
                flightinfo['timefact'] = None
            else:
                naivet = DT.datetime.strptime(flightinfo['DFACT'] + ' ' + flightinfo['TFACT'], '%d.%m.%Y %H:%M')
                flightinfo['timefact'] = pytz.timezone(zone).localize(naivet,is_dst=False)
            convertdic = {}
            for key in flightinfo:
                expectlst = ['TPLAN', 'DPLAN', 'TEXP', 'DEXP', 'TFACT', 'DFACT']
                if key in expectlst:
                    continue
                else:
                    convertdic[key.lower()] = flightinfo[key]
            convertdic['ad'] = int(convertdic['ad'])
            if convertdic['status'] is None:
                convertdic['status'] = ''
            self.append(convertdic)
            flightinfo = {}

def getxmlfromserver(filename, server, port, request):
   if int(sys.version_info[0]) == 3:
       conector = HTTPConnection(server, port)
       conector.request("GET", request)
       result = conector.getresponse()
       file = open(filename, "w")
       file.write(result.read().decode("utf-8"))
       conector.close()
       file.close()
   else:
       raise Exception("Python version less then 3")

'''
def updatedb(xmlflights, model):
    for flight in xmlflights:
        fly = model.objects.get()

        row = cursor.fetchone()
        if row is None:
            #print('insert: ', flight)
            cursor.execute("INSERT INTO flightinfosystem_flights "
                           "(fly, ad, aircraft, carrname, status, timeexp, timefact, "
                           "timeplan, portdist, punktdist) VALUES (:fly, :ad, :aircraft,"
                           ":carrname, :status, :timeexp, :timefact, :timeplan, :portdist,"
                           ":punktdist)", flight)
            cursor.fetchone()
            conn.commit()
        else:
            #print(row[0], 'update: ', flight)
            tmp = flight.copy()
            tmp['id'] = row[0]
            cursor.execute("UPDATE flightinfosystem_flights SET fly=:fly, ad=:ad, "
                           "aircraft=:aircraft, carrname=:carrname, status=:status,"
                           "timeexp=:timeexp, timefact=:timefact, timeplan=:timeplan,"
                           "portdist=:portdist, punktdist=:punktdist WHERE id=:id",
                           tmp)
            cursor.fetchone()
            conn.commit()
    cursor.execute("SELECT id, fly, timeplan FROM flightinfosystem_flights")
    rows = cursor.fetchall()
    lst = xmlflight.gettuplelst()
    for row in rows:
        if (row['fly'], row['timeplan']) not in lst:
            #print('delete ', row['id'], row['fly'], row['timeplan'])
            cursor.execute("DELETE FROM flightinfosystem_flights WHERE id=?", [row['id']])
            cursor.fetchone()
            conn.commit()

def updatemodel(xmlflights, djmodel):
    for flight in xmlflights:
        model =
        cursor.execute("SELECT id FROM flightinfosystem_flights WHERE fly=? AND timeplan=?;",(flight['fly'], flight['timeplan']))
        row = cursor.fetchone()
        if row is None:
            #print('insert: ', flight)
            cursor.execute("INSERT INTO flightinfosystem_flights "
                           "(fly, ad, aircraft, carrname, status, timeexp, timefact, "
                           "timeplan, portdist, punktdist) VALUES (:fly, :ad, :aircraft,"
                           ":carrname, :status, :timeexp, :timefact, :timeplan, :portdist,"
                           ":punktdist)", flight)
            cursor.fetchone()
            conn.commit()
        else:
            #print(row[0], 'update: ', flight)
            tmp = flight.copy()
            tmp['id'] = row[0]
            cursor.execute("UPDATE flightinfosystem_flights SET fly=:fly, ad=:ad, "
                           "aircraft=:aircraft, carrname=:carrname, status=:status,"
                           "timeexp=:timeexp, timefact=:timefact, timeplan=:timeplan,"
                           "portdist=:portdist, punktdist=:punktdist WHERE id=:id",
                           tmp)
            cursor.fetchone()
            conn.commit()
    cursor.execute("SELECT id, fly, timeplan FROM flightinfosystem_flights")
    rows = cursor.fetchall()
    lst = xmlflight.gettuplelst()
    for row in rows:
        if (row['fly'], row['timeplan']) not in lst:
            #print('delete ', row['id'], row['fly'], row['timeplan'])
            cursor.execute("DELETE FROM flightinfosystem_flights WHERE id=?", [row['id']])
            cursor.fetchone()
            conn.commit()

xmlrequests = (('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0"),
               ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,1"),
               ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0"),
               ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,1"),
             )



for request in xmlrequests:
    getxmlfromserver(xmlfile, *request)
    xmlflight.getfromxml(xmlfile)
'''

class Command(BaseCommand):
    help = 'get xml from AODB and update Flight models. This script for crontab.'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        path = os.getcwd()
        xmlfile = 'tmpxmlfile.xml'
        xmlflight = FlightsXML()
        xmlflight.getfromxml(xmlfile)
        for flight in xmlflight:
            try:
                dbflight = Flight.objects.get(fly=flight['fly'], ad=flight['ad'], timeplan=flight['timeplan'],
                                              aircraft=flight['aircraft'], portdist=flight['portdist'])
            except Flight.DoesNotExist:
                dbflight = Flight(fly=flight['fly'],
                                  timeplan=flight['timeplan'],
                                  aircraft=flight['aircraft'],
                                  portdist=flight['portdist'],
                                  punktdist=flight['punktdist'],
                                  status=flight['status'],
                                  timeexp=flight['timeexp'],
                                  timefact=flight['timefact'],
                                  carrname=flight['carrname'],
                                  ad=flight['ad'])
                dbflight.save()
                self.stdout.write('Add new record id={}: fly {} timeplan {} distination {}'.format(dbflight.pk,
                                                                                                   flight['fly'],
                                                                                                   flight['timeplan'],
                                                                                                   flight['portdist']))
            else:
                tmplstfields = []
                for field in Flight._meta.fields:
                    self.stdout.write('field {}'.format(field))
                    if getattr(dbflight, field) != flight[field]:
                        setattr(dbflight, field, flight[field])
                        tmplstfields.append(field)
                dbflight.save()
                self.stdout.write('Update record {}? this fields: {}'.format(dbflight.pk, tmplstfields))
