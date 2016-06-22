import sys
from xml.etree.ElementTree import parse
import datetime as DT
from ftplib import FTP
import pickle
if int(sys.version_info[0]) == 3:
    from http.client import HTTPConnection
else:
    raise Exception("Version python less then 3")
import sqlite3
'''
class Flights(list):
    def __init__(self):
        self = []

    def getfromxml(self, filename):
        flightinfo = {}
        tree = parse(filename)
        for fly in tree.findall('FLY'):
            flightinfo['FLY'] = fly.attrib['number']
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
                            destinetion +=  ' - '+ flightparam.text
                    continue
                flightinfo.setdefault(flightparam.tag, flightparam.text)
            flightinfo['PORTDIST'] = airportdist
            flightinfo['PUNKTDIST'] = destinetion
            #перевести дату и время в удобный формат
            if flightinfo['TPLAN'] is None or flightinfo['DPLAN'] is None:
                flightinfo['TIMEPLAN'] = None
            else:
                flightinfo['TIMEPLAN'] = DT.datetime.strptime(flightinfo['DPLAN'] + ' ' + flightinfo['TPLAN'], '%d.%m.%Y %H:%M')
            if flightinfo['TEXP'] is None or flightinfo['DEXP'] is None:
                flightinfo['TIMEEXP'] = None
            else:
                flightinfo['TIMEEXP'] = DT.datetime.strptime(flightinfo['DEXP'] + ' ' + flightinfo['TEXP'], '%d.%m.%Y %H:%M')
            if flightinfo['TFACT'] is None or flightinfo['DFACT'] is None:
                flightinfo['TIMEFACT'] = None
            else:
                flightinfo['TIMEFACT'] = DT.datetime.strptime(flightinfo['DFACT'] + ' ' + flightinfo['TFACT'], '%d.%m.%Y %H:%M')
            self.append(flightinfo)
            flightinfo = {}

    def handlenullstatus(self, flightsinfo):
        HOUR2 = DT.timedelta(seconds=7200)
        MIN40 = DT.timedelta(seconds=2400)
        MIN20 = DT.timedelta(seconds=1200)
        DEPARTPLAN = 'Вылет по плану'
        DEPARTTIMEEXP = 'Вылет по расч. времени '
        STARTCHEKIN = 'Начинается регистрация пассажиров и багажа'
        CHECKIN = 'Регистрация. Стойки: '
        BETWEENCHECKBOARD = 'Регистрация закончена. Загрузка багажа'
        BOARDING = 'Посадка пассажиров'
        UPDATETIMEDEPART = 'Уточнение времени вылета'
        ARRIVEPLAN = 'Прилет ожидается по плану'
        ARRIVEEXP = 'Прилет по расч. времени '
        #отработать пустые статусы
        for flight in self:
            if flight['STATUS'] is None:
                fly = flight['FLY']
                now = DT.datetime.now()
                #departure
                if flight['AD'] == '0':
                    if flight['TIMEEXP'] is None:
                        flight['STATUS'] = DEPARTPLAN
                    else:
                        if now < flight['TIMEEXP'] - HOUR2 and not flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = DEPARTTIMEEXP + flight['TEXP']
                        elif now < flight['TIMEEXP'] - HOUR2 and flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = CHECKIN + flightsinfo.getflightstatus(fly, 'CHECKIN')
                        elif flight['TIMEEXP'] - HOUR2 <= now <= flight['TIMEEXP'] - MIN40 and not flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = STARTCHEKIN
                        elif flight['TIMEEXP'] - HOUR2 <= now <= flight['TIMEEXP'] - MIN40 and flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = CHECKIN + flightsinfo.getflightstatus(fly, 'CHECKIN')
                        elif flight['TIMEEXP'] - MIN40 < now <= flight['TIMEEXP'] - MIN20:
                            flight['STATUS'] = BETWEENCHECKBOARD
                        elif flight['TIMEEXP'] - MIN20 < now <= flight['TIMEEXP']:
                            flight['STATUS'] = BOARDING
                        else:
                            flight['STATUS'] = UPDATETIMEDEPART
                #arrivels
                else:
                    if flight['TIMEEXP'] is None:
                        flight['STATUS'] = ARRIVEPLAN
                    else:
                        flight['STATUS'] = ARRIVEEXP + flight['TEXP']

    def __str__(self):
        st = ''
        for elem in self:
            st += str(elem) + '\n'
        return st

    def today(self):
        result = Flights()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date():
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date():
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date():
                        result.append(flight)
        return result

    def yesterday(self):
        result = Flights()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                        result.append(flight)
        return result

    def tomorrow(self):
        result = Flights()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                        result.append(flight)
        return result

    def save(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self, f)
        return True

    def load(self, filename):
        try:
            f = open(filename, 'rb')
        except FileNotFoundError:
            return False
        self = pickle.load(f)
        return True

    def isdifferent(self, picklefile):
        flag = False
        try:
            f = open(picklefile, 'rb')
        except FileNotFoundError:
            return True
        oldinfo = pickle.load(f)
        for old, new in zip(oldinfo, self):
            if old != new:
                flag = True
                break
        return flag

    def converttoHTML(self, template):

        partlines = ''
        parts = []
        fdiscript = open(template, 'r')
        for line in fdiscript:
            if line.find('<!-- separator -->') != -1:
                parts.append(partlines)
                partlines = ''
            else:
                partlines += line
        parts.append(partlines)
        fdiscript.close()
        if len(parts) < 3:
            raise Exception("Separators in template less then 2. The pattern should be divided into three parts")
        if len(parts) > 3:
            raise Exception("Separators in template more then 2. The pattern should be divided into three parts")
        st = ''
        for flight in self:
            st += parts[1].format(**flight)
        parts[1] = st
        st = ''.join(parts)
        return st

    def getflightsparametr(self,param):
        result = []
        for flight in self:
            result.append(flight[param])
        return result

def savetofile(str, filename, codepage='utf-8'):
        f = open(filename, 'w', encoding=codepage)
        f.write(str)
        f.close()
        return True

def sendfilestoftp(filenamelist, server, username=None, password=None):
    for filename in filenamelist:
        ftp = FTP(server, username, password)
        file = open(filename, 'rb')
        ftp.storlines('STOR '+filename, file)
        file.close()
        ftp.close()
    return True

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

def getflighttime(flight):
    return flight['TIMEPLAN']

def updatedb(db, newflights):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timeplan FROM flightinfosystem_flights")
    oldinfo = {}
    for id, tm in cursor:
        print(id, tm)
        oldinfo[id] = DT.datetime.strptime(tm,'%Y-%m-%d %H:%M:%S')
    for flight in newflights:
        ad = int(flight['AD'])
        fly = flight['FLY']
        punktdist = flight['PUNKTDIST']
        portdist = flight['PORTDIST']
        aircraft = flight['AIRCRAFT']
        carrname = flight['CARRNAME']
        if flight['STATUS'] is None:
            status = ''
        else:
            status = flight['STATUS']
        timeplan = DT.datetime.strftime(flight['TIMEPLAN'], '%Y-%m-%d %H:%M:%S')
        if flight['TIMEEXP'] is None:
            timeexp = None
        else:
            timeexp = DT.datetime.strftime(flight['TIMEEXP'], '%Y-%m-%d %H:%M:%S')
        if flight['TIMEFACT'] is None:
            timefact = None
        else:
            timefact = DT.datetime.strftime(flight['TIMEFACT'], '%Y-%m-%d %H:%M:%S')

        if timeplan in list(oldinfo.values()):
            #update db row
            for key in oldinfo:
                if oldinfo[key] == timeplan:
                    id = key
            cursor.execute("UPDATE flightinfosystem_flights SET (fly=?, ad=?, punktdist=?, portdist=?, aircraft=?, "
                           "carrname=?, status=?, timeplan=?, timeexp=?, timefact=?) WHERE id=?",
                           [ad, fly, punktdist, portdist, aircraft, carrname, status, timeplan, timeexp, timefact, id])
            print('update',cursor.fetchall())
        else:
            #insert row in db
            cursor.execute("INSERT INTO flightinfosystem_flights (fly, ad, punktdist, portdist, aircraft, carrname,"
                           "status, timeplan, timeexp, timefact) VALUES (?,?,?,?,?,?,?,?,?,?)",
                           [fly, ad, punktdist, portdist, aircraft, carrname, status, timeplan, timeexp, timefact])
            print('insert',cursor.fetchall())

    cursor.execute("select id, timeplan from flightinfosystem_flights")
    tupllist = cursor.fetchall()
    for id, tplan in tupllist:
        oldtimeplan = DT.datetime.strptime(tplan,'%Y-%m-%d %H:%M:%S')
        if oldtimeplan not in newflights.getflightsparametr('TIMEPLAN'):
            #delete
            cursor.execute("DELETE FROM flightinfosystem_flights WHERE id=?",[id])
            print('delete', cursor.fetchall())
    conn.commit()
    conn.close()
'''

class FlightsDB(dict):
    def __init__(self):
        self = {}

    def getfromdb(self, dbfile):
        conn = sqlite3.connect(dbfile)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flightinfosystem_flights")
        info = {}
        dbrow = cursor.fetchone()
        while dbrow is not None:
            for key in dbrow.keys():
                if key != 'id':
                    info[key] = dbrow[key]
                id = dbrow['id']
            self.setdefault(id, info)
            info = {}
            dbrow = cursor.fetchone()

class FlightsXML(list):
    def __init__(self):
        self = []

    def getfromxml(self, xmlfile):
        '''начать парсить xml файл в удобную структуру'''
        flightinfo = {}
        tree = parse(xmlfile)
        for fly in tree.findall('FLY'):
            flightinfo['fly'] = fly.attrib['number']
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
            # перевести дату и время в удобный формат
            if flightinfo['TPLAN'] is None or flightinfo['DPLAN'] is None:
                flightinfo['timeplan'] = None
            else:
                flightinfo['timeplan'] = DT.datetime.strptime(flightinfo['DPLAN'] + ' ' + flightinfo['TPLAN'],
                                                              '%d.%m.%Y %H:%M')
            if flightinfo['TEXP'] is None or flightinfo['DEXP'] is None:
                flightinfo['timeexp'] = None
            else:
                flightinfo['timeexp'] = DT.datetime.strptime(flightinfo['DEXP'] + ' ' + flightinfo['TEXP'],
                                                             '%d.%m.%Y %H:%M')
            if flightinfo['TFACT'] is None or flightinfo['DFACT'] is None:
                flightinfo['timefact'] = None
            else:
                flightinfo['timefact'] = DT.datetime.strptime(flightinfo['DFACT'] + ' ' + flightinfo['TFACT'],
                                                              '%d.%m.%Y %H:%M')
            convertdic = {}
            for key in flightinfo:
                expectlst = ['TPLAN', 'DPLAN', 'TEXP', 'DEXP', 'TFACT', 'DFACT']
                if key in expectlst:
                    continue
                else:
                    convertdic[key.lower()] = flightinfo[key]
            for key in ['timeplan','timeexp','timefact']:
                if convertdic[key] is not None:
                    convertdic[key] = DT.datetime.strftime(convertdic[key], '%Y-%m-%d %H:%M:%S')
            convertdic['ad'] = int(convertdic['ad'])
            if convertdic['status'] is None:
                convertdic['status'] = ''
            self.append(convertdic)
            flightinfo = {}

    def gettuplelst(self):
        lst = []
        for flight in self:
            lst.append((flight['fly'], flight['timeplan']))
        return lst

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


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


def updatedb(xmlflights, dbfile):
    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    for flight in xmlflights:
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

xmlfile = 'tmpxmlfile.xml'
xmlflight = FlightsXML()
for request in xmlrequests:
    getxmlfromserver(xmlfile, *request)
    xmlflight.getfromxml(xmlfile)

dbfile ='../db.sqlite3'
#dbflight = FlightsDB()
#dbflight.getfromdb(dbfile)
updatedb(xmlflight, dbfile)