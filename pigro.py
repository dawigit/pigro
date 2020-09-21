# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from widget import *
import time               # Import time library
from datetime import datetime
import locale
import os
import yaml
from moon import get_moon
from moon import get_phase
from moon import set_location
import Adafruit_PCA9685
import adafruit_dht as dht0
import w1thermsensor
try:
    w1 = w1thermsensor.W1ThermSensor()
except:
    w1 = None
import threading
from threading import Timer
from HIH7130 import HIH7130
try:
    HIH7130 = HIH7130()
except:
    HIH7130 = None

os.environ['DE'] = 'EU/CET-1'
time.tzset()
dto=datetime.now()
city = "Rosenheim, Germany"
set_location(city)
K_AUTO_TEMP = 31
K_PWM_REVERSED = False

idpercentpwma = 0
idclockstart = 0
idclockstop = 0

on_hour = 7
on_minute = 0
off_hour = 19
off_minute = 0

gc = 0
errors = []

Lpercent = []
for i in  range(11):
    Lpercent.append('{:>3}'.format(str(i*10)))

percent2 = []
for i in range(21):
    percent2.append('{:>3}'.format(str(i*10)))
l4k = []
for i in range(4096):
    l4k.append('{:>4}'.format(str(i)))

dht = dht0.DHT22(23)

dhtv = []
def dht_get():
    global dhtv
    try:
        h = dht.humidity
        t = dht.temperature
        dhtv = [h,t]
    except RuntimeError as error:
        errors.append(error.args)
        dhtv = [0,0]

dht_get()

def get_hih(m):
    global hih_result
    if HIH7130:
        hih_result = HIH7130.read_hum_temp()
    else:
        hih_result = {'h' : 50.0, 'c' : 25.0}
    if m=='h':
        return "{0:3.2f} % RH".format(hih_result['h'])
    if m=='c':
        return "{0:3.2f} °C".format(hih_result['c'])
    if m=='H':
        return hih_result['h']
    if m=='C':
        return hih_result['c']

S_UPDATE = "🔄 "
S_OK     = "✅ "
S_MQTT = '📡 '
S_VEGI = '🌿'
S_BLOOM = '🌼'
S_DAY = '🌞'
S_NIGHT = '🌙'
S_WATER = '💧'
S_THERMO = "🌡"
S_HUMIDITY = "🌫💧"
S_TORCH = "🔦"
S_LAMP =  " 💡 "
S_SLEEP = "😴 "
S_RADIATION = "☢"
S_RISE = "📈"
S_FALL = "📉"
S_WRENCH = "🔧 "
S_SPACE = " "
S_SPACE2 = "  "
S_SPACE3 = "   "


L_LIGHT = " PWM0 💡 "
L_PIGROPRO = "PiGro"
L_LIGHTON = "light on"
L_LIGHTOFF = "light off"
L_MAINTENANCE = "maintenance "


K_T1 = 1
K_T2 = 2
K_T3 = 3
K_T4 = 4

K_DHTH = 1
K_DHTT = 2

K_PWM_OUT = 15


daynightmodelist = ["12/12 🌼","18/6 🌿"]
daynightmode = 0

DEV = True
UFREQ = 5
MAINTENANCETIME = 10
power_on = False
maintenance = False

class PG():
    def __init__(self, y, x):
         self.x = x
         self.y = y
pg = PG(32,79)
pos_status = PG(2,2)
pos_pigropro = PG(2,6)
pos_datetime = PG(2, 40)
pos_moon = PG(4,40)
pos_temperature = PG(8,40)
pos_lightselect = PG(5,2)
pos_pwm = PG(20,2)
pos_dnmode = PG(5,12)
pos_maintenance = PG(4,20)
pos_clock = PG(11,13)

suw = SuWidget(scr)

pwmlight = 0
pwmv = [0]*16
pwms = [0]*16
pwmid = [0]*16

pwmv[0]=50
pwmv[4]=0
pwmv[13]=0
pwmv[14]=0
pwmv[15]=80

pwms[0]=5
pwms[4]=0
pwms[13]=0
pwms[14]=0
pwms[15]=8

try:
    file = open(r'./pigro.yaml', 'r')
    if file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        if config:
            pwmlight = int(config['pwmlight'])
            pwms = config['pwms']
            pwmv = config['pwmv']
            daynightmode = int(config['daynightmode'])
            on_hour = int(config['on'].split(':')[0])
            on_minute = int(config['on'].split(':')[1])
            off_hour = int(config['off'].split(':')[0])
            off_minute = int(config['off'].split(':')[1])
            power_on = config['power']
            maintenance = config['maintenance']
            #config = yaml.dump(dict_file, file)
except:
    None

PWMFREQ = 1000
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(PWMFREQ)

def set_pwm(id,value):
    global power_on, maintenance
    if type(value) == str:
        value = int(value)
    if id == 0 and power_on == False:
        value = 0
    if id == 0:
        if maintenance == True and power_on == True:
            value = 20
        if K_PWM_REVERSED:
            value = 100 - value

    v = int((4095*value)/100)
    pwm.set_pwm(id,0,v)

for i in range(16):
    set_pwm(i,0)

def set_pwm2(id,a,b):
    global power_on
    if type(a) == str:
        a = int(a)
    if type(b) == str:
        b = int(b)
    if id == 0 and power_on == False:
        pwm.set_pwm(0,0,0)
    else:
        pwm.set_pwm(0,a,b)

def wpwm_change(index,value,selected):
    global pwmv, pwms
    pwmv[index] = value
    pwms[index] = selected
    set_pwm(index,value)

w1t = [0,0,0,0]
if w1:
    w1s = w1.get_available_sensors()
else:
    w1s = 0
def w1_gettemparray():
    global w1t,w1s
#    global w1t
#    w1t = [0,0,0,0]
    try:
        l = len(w1s)
        if l > 0:
            for i in range(l):
                w1t[i] = w1s[i].get_temperature()
        else:
            w1t = [0,0,0,0]
    except:
        w1t = [0,0,0,0]
w1_gettemparray()


m = '🌞'
lasttimer = None
lastmaintenance = None
lasttimer_pwm = ''
#city = 'Munich'

def check_onoff():
    global power_on,idpercentpwma,idclockstart,idclockstop
    t = datetime.now()
    c = suw.get_clock(idclockstart)
    ton = int(c.split(":")[0])*60+int(c.split(":")[1])
    c = suw.get_clock(idclockstop)
    toff = int(c.split(":")[0])*60+int(c.split(":")[1])
    tnow = t.hour*60+t.minute
#    suw.scr.addstr(0,0,"on: {0:} off: {1:} now: {2:} {3:}".format(ton,toff,tnow,type(ton)))
    if tnow >= ton and tnow <= toff:
        power_on = True
        set_pwm(0,int(suw._wlist[idpercentpwma].get_selected()*10))
    else:
        power_on = False
        set_pwm(0,0)
        return False

def getmoon():
    return "{0:}".format(get_moon())
def getphase():
    return "{0:3.2f}%".format(get_phase())

def get_w1t(i):
    global w1t,gc
    gc += 1
#    return str.format("{0:3.2f} °C ({1:})", w1t[i-1],gc)
    if i < len(w1t)+1:
        return str.format("{0:3.2f} °C", w1t[i-1])
    else:
        return str.format("{0:3.2f} °C", 0)

def get_dht(i):
    global dhtv,gc
    gc+=1
    if i == K_DHTH:
#        return str.format("{0:3.2f} % ({1:})",dhtv[0],gc)
        return str.format("{0:3.2f} %",dhtv[K_DHTH-1])
    if i == K_DHTT:
#        return str.format("{0:3.2f} °C ({1:})",dhtv[1],gc)
        return str.format("{0:3.2f} °C",dhtv[K_DHTT-1])

def update_onofflabel():
    global power_on
    return S_LAMP if power_on else S_SLEEP

def update_maintenance():
    global maintenance
    return S_WRENCH if maintenance else S_SPACE2

suw.rect(0, 0, 79, 32)
suw.add_widgetlabel(L_LIGHT, pos_lightselect.x, pos_lightselect.y-1)
idprometheus = suw.add_widgetlabelvalue(L_PIGROPRO, pos_pigropro.x, pos_pigropro.y, S_SLEEP, update_onofflabel)
idmaintenance = suw.add_widgetlabelvalue(L_MAINTENANCE, pos_maintenance.x, pos_maintenance.y, S_WRENCH, update_maintenance)
idpercentpwma = suw.add_widgetselect(Lpercent,pos_lightselect.x,pos_lightselect.y,W_NOCIRCLE,pwmlight,pwmlight)
iddaynightmode = suw.add_widgetselect(daynightmodelist,pos_dnmode.x,pos_dnmode.y,W_NOCIRCLE,daynightmode,daynightmode)

suw.add_widgetlabel(L_LIGHTON, pos_clock.x,pos_clock.y-1)
idclockstart = suw.add_clock(pos_clock.x,pos_clock.y,on_hour,on_minute)
suw.add_widgetlabel(L_LIGHTOFF, pos_clock.x,pos_clock.y+2)
idclockstop = suw.add_clock(pos_clock.x,pos_clock.y+3,off_hour,off_minute)

idtempupper =   suw.add_widgetlabelvalue("{0:} board 1: ".format(S_THERMO),pos_temperature.x,pos_temperature.y, get_w1t(K_T1), get_w1t, K_T1)
idtempboarda =  suw.add_widgetlabelvalue("{0:} board 2: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+2, get_w1t(K_T2), get_w1t, K_T2)
idtempboardb =  suw.add_widgetlabelvalue("{0:} board 3: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+4, get_w1t(K_T3), get_w1t, K_T3)
idtempexterior= suw.add_widgetlabelvalue("{0:} board 4: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+6, get_w1t(K_T4), get_w1t, K_T4)
iddh = suw.add_widgetlabelvalue("{0:<6} dht: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+10, get_dht(K_DHTT), get_dht, K_DHTT)
iddt = suw.add_widgetlabelvalue("{0:<5} dht: ".format(S_HUMIDITY),pos_temperature.x,pos_temperature.y+12, get_dht(K_DHTH), get_dht, K_DHTH)
iddh = suw.add_widgetlabelvalue("{0:<6} dht: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+10, get_dht(K_DHTT), get_dht, K_DHTT)
iddt = suw.add_widgetlabelvalue("{0:<5} dht: ".format(S_HUMIDITY),pos_temperature.x,pos_temperature.y+12, get_dht(K_DHTH), get_dht, K_DHTH)

idhiht = suw.add_widgetlabelvalue("{0:<6} hih: ".format(S_THERMO),pos_temperature.x,pos_temperature.y+15, get_hih('c'), get_hih, 'c')
idhihh = suw.add_widgetlabelvalue("{0:<5} hih: ".format(S_HUMIDITY),pos_temperature.x,pos_temperature.y+16, get_hih('h') , get_hih, 'h')


idmoon = suw.add_widgetlabelvalue("moon: ", pos_moon.x, pos_moon.y, getmoon(), getmoon)
idphase = suw.add_widgetlabelvalue(" / ", pos_moon.x+10, pos_moon.y, getphase(), getphase)

vh = 10

for i in range(1,16):
    y = int(i/4)
    x = int(i%4)
    pwmid[i] = suw.add_widgetroller(Lpercent, pos_pwm.x+(5*x), pos_pwm.y+(3*y),W_FRAME+W_NOCIRCLE+W_LIVE,pwms[i],pwms[i])
    suw.set_onchange(pwmid[i], wpwm_change, i)
    set_pwm(i,pwmv[i])


def set_clockonmode(arg,mode,dum):
    #suw.scr.addstr(30,2,mode)
    s = suw.get_clock(idclockstart)
    h = int(s.split(':')[0])+(12 if mode == daynightmodelist[0] else 18)
    if h > 23:
        h-=24
    m = int(s.split(':')[1])
    suw.set_clock(idclockstop, h, m)
    suw.update(idclockstop)

def update_datetime():
    suw.scr.addstr(pos_datetime.y, pos_datetime.x, "{0:}".format(datetime.now().strftime('%Y-%m-%d  –  %H:%M:%S')))

#idpercentpwmb = suw.add_widgetroller(percent,15,15,W_FRAME+W_NOCIRCLE+W_LIVE,4,3,1,4)
suw.set_onchange(iddaynightmode, set_clockonmode)
suw.set_onchange(idpercentpwma,wpwm_change,0)
suw.focus(idpercentpwma)

counter = 0
automatique_counter = 0

def update():
    global counter
    suw.scr.addstr(pos_status.y, pos_status.x,S_UPDATE)
    update_datetime()
    suw.scr.refresh()
    counter += 1
    if counter == 5:
        dht_get()
        #w1_gettemparray()
        counter = 0
    suw.update_all()
    suw.scr.addstr(pos_status.y, pos_status.x,S_OK)
    suw.scr.refresh()



def timed_update():
    automatique()
    update()
    check_onoff()
    setClock()

def check_maintenance():
    global maintenance
    if maintenance == True:
        maintenance = False
        update()


def setClock():
    global lasttimer
    ti = Timer(UFREQ*60, timed_update)
    ti.start()
    lasttimer = ti

def setMaintenance():
    global lastmaintenance
    if lastmaintenance:
        lastmaintenance.cancel()
    tim = Timer(MAINTENANCETIME*60, check_maintenance)
    tim.start()
    lastmaintenance = tim

def automatique():
    global automatique_counter
    automatique_counter += 1
    if automatique_counter > 9:
        automatique_counter = 0
    else:
        return
    w1_gettemparray()
    h = float(get_hih('H'))
    td = 0
    tdiv = 0
    for t in w1t:
        if t > 0:
            td += t
            tdiv += 1
    if tdiv > 0:
        td /= tdiv
    if td > 0:
        if td > 31:
            suw._wlist[pwmid[K_PWM_OUT]].movecursor(1)
        if td < 26 and h < 50:
            if suw._wlist[pwmid[K_PWM_OUT]].selected > 4:
                suw._wlist[pwmid[K_PWM_OUT]].movecursor(-1)
        if td > K_AUTO_TEMP:
            if suw._wlist[idpercentpwma].selected > 5:
                suw._wlist[idpercentpwma].movecursor(-1)
                suw._wlist[idpercentpwma].select()
        if td < K_AUTO_TEMP:
            suw._wlist[idpercentpwma].movecursor(1)
            suw._wlist[idpercentpwma].select()

    if h > 60:
        suw._wlist[pwmid[K_PWM_OUT]].movecursor(1)
#
#    if dhtv[K_DHTH-1] < 80 and not dhtv[K_DHTH-1] == 0:
#        if w1t[K_TEXTERIOR-1] <= 25:
#            suw._wlist[idpercentpwma].movecursor(1)
#            suw._wlist[idpercentpwma].select()
#
#    if w1t[K_T1] > 28:
#        suw._wlist[pwmid[K_PWM_OUT]].movecursor(1)
#    if w1t[K_TUPPER] < 25:
#        if suw._wlist[pwmid[K_PWM_OUT]].selected > 6:
#            suw._wlist[pwmid[K_PWM_OUT]].movecursor(-1)

def save():
    configsave = {'pwms' : pwms,
    'pwmv' : pwmv,
    'pwmlight' : suw._wlist[idpercentpwma].get_selected(),
    'daynightmode' : suw._wlist[iddaynightmode].get_selected(),
    'on' : str(suw.get_clock(idclockstart)),
    'off' : str(suw.get_clock(idclockstop)),
    'power' : power_on,
    'maintenance' : maintenance
    }
    with open(r'./pigro.yaml', 'w') as file:
        config = yaml.dump(configsave, file)

timed_update()
update()
key = ''
while key != ord('q'):
    key = suw.scr.getch()
    suw.onkeyboard(key)
    if key == ord(' '):
        timed_update()
    if key == ord('t'):
        timed_update()
    if key == ord('r'):
        suw.scr.clear();
        suw.rect(0, 0, 79, 32)
        update()
    if key == ord('s'):
        save()
    if key == ord('l'):
        w1 = w1thermsensor.W1ThermSensor()
        w1s = w1.get_available_sensors()
    if key == ord('m'):
        if maintenance == False:
            setMaintenance()
        maintenance = not maintenance

        update()
        set_pwm(0,pwmv[0])
save()
suw.quit()
lasttimer.cancel()
