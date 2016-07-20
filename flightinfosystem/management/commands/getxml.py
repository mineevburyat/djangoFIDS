import datetime as DT
import sys
from xml.etree.ElementTree import parse

import pytz
from django.core.management.base import BaseCommand

from flightinfosystem.models import Flight, FlightStatus, EventLog

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


class Command(BaseCommand):
    help = 'get xml from AODB and update Flight models. This script for crontab.'

    #def add_arguments(self, parser):
    #    parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):

        xmlfile = 'tmpxmlfile.xml'
        xmlurls = (('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0"),
                   ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0"))
        xmlflights = FlightsXML()
        for request in xmlurls:
            getxmlfromserver(xmlfile, *request)
            xmlflights.getfromxml(xmlfile)

        #xmlflights.getfromxml(xmlfile)
        for xmlflight in xmlflights:
            try:
                dbflight = Flight.objects.get(fly=xmlflight['fly'], ad=xmlflight['ad'], timeplan=xmlflight['timeplan'],
                                              aircraft=xmlflight['aircraft'], portdist=xmlflight['portdist'])
            except Flight.DoesNotExist:
                dbflight = Flight(fly=xmlflight['fly'],
                                  timeplan=xmlflight['timeplan'],
                                  aircraft=xmlflight['aircraft'],
                                  portdist=xmlflight['portdist'],
                                  punktdist=xmlflight['punktdist'],
                                  status=xmlflight['status'],
                                  timeexp=xmlflight['timeexp'],
                                  timefact=xmlflight['timefact'],
                                  carrname=xmlflight['carrname'],
                                  ad=xmlflight['ad'])
                dbflight.save()
                text = 'id={}: fly={}, timeplan={}'.format(dbflight.pk, xmlflight['fly'], xmlflight['timeplan'])
                eventlog = EventLog(fly=dbflight, event_id=1, descript=text)
                eventlog.save()
                flightstatus = FlightStatus(fly=dbflight)
                flightstatus.save()
                self.stdout.write('Add flight' + text)

            else:
                tmplstfields = []
                clsfields = Flight._meta.local_fields
                for field in [clsfield.name for clsfield in clsfields]:
                    if field == 'id' or field == 'pk':
                        continue
                    else:
                        if getattr(dbflight, field) != xmlflight[field]:
                            setattr(dbflight, field, xmlflight[field])
                            tmplstfields.append(field)
                if len(tmplstfields) > 0:
                    dbflight.save()
                    text = 'Update fields: {}'.format(tmplstfields)
                    eventlog = EventLog(event_id=2, fly=dbflight, descript=text)
                    eventlog.save()
                    self.stdout.write('Update flight {}! '.format(dbflight.pk) + text)
