# -*- coding: utf-8 -*-
#!/usr/bin/env python3

NOMOON = True

import time               # Import time library
from datetime import datetime
import locale
import os
import yaml
import Adafruit_PCA9685
import threading
from threading import Timer
from sensors import sen
if not NOMOON:
    from moon import get_moon
    from moon import get_phase
    from moon import set_location
    def getmoon():
        return "{0:}".format(get_moon())
    def getphase():
        return "{0:3.2f}%".format(get_phase())
    city = "Rosenheim, Germany"
    set_location(city)

from widget import *

os.environ['DE'] = 'EU/CET-1'
time.tzset()
dto=datetime.now()

K_UPDATE_COUNTER = 5 # sensors are read every 5th update

K_AUTO_TEMP = 31
K_PWM_REVERSED = False

K_MAINTENANCE_LIGHT = 20    #pwm value for maintenance mode


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
MAINTENANCETIME = 20
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
pos_sens = PG(8,40)
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
            value = K_MAINTENANCE_LIGHT
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



m = '🌞'
lasttimer = None
lastmaintenance = None
lasttimer_pwm = ''

def check_onoff():
    global power_on,idpercentpwma,idclockstart,idclockstop
    t = datetime.now()
    c = suw.get_clock(idclockstart)
    ton = int(c.split(":")[0])*60+int(c.split(":")[1])
    c = suw.get_clock(idclockstop)
    toff = int(c.split(":")[0])*60+int(c.split(":")[1])
    tnow = t.hour*60+t.minute
    if toff < ton:
        toff+=24*60
#    suw.scr.addstr(0,0,"on: {0:} off: {1:} now: {2:} {3:}".format(ton,toff,tnow,type(ton)))
    if tnow >= ton and tnow <= toff:
        power_on = True
        set_pwm(0,int(suw._wlist[idpercentpwma].get_selected()*10))
    else:
        power_on = False
        set_pwm(0,0)
        return False


def get_w1(i=0):
    key = 'W1'+str(i)
    if key in sen.sensors.keys():
        w1t = sen.sensors['W1'+str(i)].get()
    else:
        return 'N/A'
    return str.format("{0:3.2f} °C", w1t)

def get_dht(m):
    if 'DHT' in sen.sensors.keys():
        if m == 'r':
            value = sen.sensors['DHT'].read()
        if m == 'h':
            return str.format("{0:3.2f} %",value['h'])
        if m == 'c':
            return str.format("{0:3.2f} °C",value['c'])
    else:
        return 'N/A'

#get_hih(mode)
#'r' read sensor values
#'c'/'h' retrieve values from hih_result (stored sensor values)
def get_hih(m):
    if 'HIH' in sen.sensors.keys():
        if m=='r':
            sen.sensors['HIH'].read()
        if m=='h':
            return "{0:3.2f} % RH".format(sen.sensors['HIH'].get()['h'])
        if m=='c':
            return "{0:3.2f} °C".format(sen.sensors['HIH'].get()['c'])
        if m=='H':
            return sen.sensors['HIH'].get()['h']
        if m=='C':
            return sen.sensors['HIH'].get()['c']
    else:
        return 'N/A'

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

lc = 1
if 'W10' in sen.sensors.keys():
    suw.add_widgetlabelvalue("{0:} W10: ".format(S_THERMO),pos_sens.x,pos_sens.y, get_w1(0), get_w1, 0)
if 'W11' in sen.sensors.keys():
    suw.add_widgetlabelvalue("{0:} W11: ".format(S_THERMO),pos_sens.x,pos_sens.y+lc, get_w1(1), get_w1, 1)
    lc+=1
if 'DHT' in sen.sensors.keys():
    suw.add_widgetlabelvalue("{0:} DHT: ".format(S_THERMO),pos_sens.x,pos_sens.y+lc, get_dht('c'), get_dht, 'c')
    lc+=1
    suw.add_widgetlabelvalue("{0:} DHT: ".format(S_HUMIDITY),pos_sens.x,pos_sens.y+lc, get_dht('h'), get_dht, 'h')
    lc+=1
if 'HIH' in sen.sensors.keys():
    suw.add_widgetlabelvalue("{0:} HIH: ".format(S_THERMO),pos_sens.x,pos_sens.y+lc, get_hih('c'), get_hih, 'c')
    lc+=1
    suw.add_widgetlabelvalue("{0:} HIH: ".format(S_HUMIDITY),pos_sens.x,pos_sens.y+lc, get_hih('h') , get_hih, 'h')
    lc+=1
# could add more Sensors
if not NOMOON:
    suw.add_widgetlabelvalue("moon: ", pos_moon.x, pos_moon.y, getmoon(), getmoon)
    suw.add_widgetlabelvalue(" / ", pos_moon.x+10, pos_moon.y, getphase(), getphase)

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
    if counter == K_UPDATE_COUNTER:
        get_dht('r')
        get_hih('r')    #read new values from sensors
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

    h = float(get_hih('H'))
    td = float(get_hih('C'))

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
