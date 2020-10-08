# -*- coding: utf-8 -*-
#!/usr/bin/env python3

NOMOON = True
NOAUTO = False
ROW1 = 4
ROW2 = 2
from base import BaseUtil
import time               # Import time library
from datetime import datetime
import locale
import os
import yaml
import Adafruit_PCA9685
import threading
from threading import Timer
from sensors import sen
from sensors import W1
from pwm import PWM,PWMMode,rpwm

if len(sen.sensors) == 0:
    NOAUTO = True

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

K_UPDATE_COUNTER = 2 # sensors are read every 5th update
K_AUTO_TEMP = 31
K_MAINTENANCE_LIGHT = 20    #pwm value for maintenance mode


m = '🌞'
lasttimer = None
lastmaintenance = None
lasttimer_pwm = ''


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
S_CURSOR = "👉"
S_CLOCK = "⏰"
S_FAN = " 🌪 "


L_LIGHT = " PWM0 💡 "
L_PIGRO = "PiGro"
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

truefalselist = ["False","True "]
pwmreversed = 0
daynightmodelist = ["12/12 🌼","18/6 🌿"]
daynightmode = 0

DEV = True
UFREQ = 5
MAINTENANCETIME = 20
power_on = False
maintenance = False


pg = WPos(79,32)
pos_status = WPos(2,2)
pos_pigropro = WPos(6,2)
pos_datetime = WPos(40,2)
pos_moon = WPos(40,4)
pos_sens = WPos(44,8)
pos_lightselect = WPos(2,5)
pos_pwm = WPos(2,20)
pos_dnmode = WPos(12,5)
pos_maintenance = WPos(20,2)
pos_clock = WPos(13,11)



def wpwm_change(index,value,selected):
    rpwm.set(index,value)

def update_onofflabel():
    global power_on
    return S_LAMP if power_on else S_SLEEP

def update_maintenance():
    global maintenance
    return S_WRENCH if maintenance else S_SPACE2

def check_onoff(port=0):
    global power_on
    t = datetime.now()
    c = suw.get_clock_time("CLOCK"+str(port)+"ON")
    ton = int(c.split(":")[0])*60+int(c.split(":")[1])
    c = suw.get_clock_time("CLOCK"+str(port)+"OFF")
    toff = int(c.split(":")[0])*60+int(c.split(":")[1])
    tnow = t.hour*60+t.minute
    if toff < ton:
        toff+=24*60
    if tnow >= ton and tnow <= toff:
        power_on = True
        rpwm.enable(port)
        rpwm.set(port,int(suw._wlist["PWM"+str(port)].get_selected()*10))
    else:
        power_on = False
        rpwm.disable(port)


def get_w1(m):
    if m == 'r':
        for s in sen.sensors.values():
            if type(s) is W1:
                s.read()
        return
    key = 'W1'+str(m)
    if key in sen.sensors.keys():
        w1t = sen.sensors['W1'+str(m)].get()
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

suw = SuWidget()
config = {}
try:
    file = open(r'./config.yaml', 'r')
    if file:
        config = yaml.load(file, Loader=yaml.FullLoader)
except:
    config['pwm'] = rpwm.get_config()
    for i in range(ROW1*ROW2):
        inv = 0
        if i==0 or i==1:
            inv = 1
        config['PWM'+str(i)] = 0
        config['CLOCK'+str(i)+'ON'] = [7,0]
        config['CLOCK'+str(i)+'OFF'] = [19,0]
        config['PWM'+str(i)+'INV'] = inv


suw.rect(0, 0, 79, 40)
suw.add_widgetlabelvalue("PIGRO", L_PIGRO, pos_pigropro, update_onofflabel)
suw.add_widgetlabelvalue("MAINTENANCE", L_MAINTENANCE, pos_maintenance, update_maintenance)
p = WPos(6,4)
slist = [S_LAMP,S_LAMP,S_FAN,S_FAN]
for j in range(ROW2):
    for i in range(ROW1):
        if i == 0:
            p.setnext(10,2)
        else:
            p.setnext(10,2)

        if i == 0:
            suw.add_widgetroller("PWM"+str(i+j*ROW1), Lpercent, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)],config['PWM'+str(i+j*ROW1)],0,1,[slist[i],WPos(-4,1), "PWM"+str(i+j*ROW1)+"-"+str(i+j*ROW1+3),WPos(0,-1)])
        else:
            suw.add_widgetroller("PWM"+str(i+j*ROW1), Lpercent, p, WMode.FNL,config['PWM'+str(i+j*ROW1)],config['PWM'+str(i+j*ROW1)],0,1,[slist[i],WPos(-4,1)])
        p.nextposx()
        if i == 0 and j==0:
            suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"ON", p,
                config['CLOCK'+str(i+j*ROW1)+'ON'][0],config['CLOCK'+str(i+j*ROW1)+'ON'][1],[" ⏰ ",WPos(-4,1), "On/Off",WPos(0,-1)])
        else:
            suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"ON", p,
                config['CLOCK'+str(i+j*ROW1)+'ON'][0],config['CLOCK'+str(i+j*ROW1)+'ON'][1],[" ⏰ ",WPos(-4,1)])
        p.nextposx()
        suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"OFF", p,
            config['CLOCK'+str(i+j*ROW1)+'OFF'][0],config['CLOCK'+str(i+j*ROW1)+'OFF'][1])
        p.nextposx()
        if i == 0 and j==0:
            suw.add_widgetroller("PWM"+str(i+j*ROW1)+"INV", truefalselist, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)+'INV'],config['PWM'+str(i+j*ROW1)+'INV'],0,1,["Inverse",WPos(0,-1)])
        else:
            suw.add_widgetroller("PWM"+str(i+j*ROW1)+"INV", truefalselist, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)+'INV'],config['PWM'+str(i+j*ROW1)+'INV'],0,1)
        p.x = p.ix
        p.nextposy()
    p.setnext(0,3)
    p.nextpos()

rpwm.add(0,10,PWMMode.default,0,100)
rpwm.add(1,0,PWMMode.RERE,0,80)
for i in range(2,ROW1*ROW2):
    rpwm.add(i,0)
for i in range(ROW1*ROW2):
    suw.set_onchange("PWM"+str(i),wpwm_change,i)

pos_sens.setnext(0,1)
pos_moon.setnext(10,0)

if 'W10' in sen.sensors.keys():
    suw.add_widgetlabelvalue("W1T0", "{0:} W10: ".format(S_THERMO),pos_sens, get_w1, 0)
    pos_sens.nextpos()
if 'W11' in sen.sensors.keys():
    suw.add_widgetlabelvalue("W1T1", "{0:} W11: ".format(S_THERMO),pos_sens, get_w1, 1)
    pos_sens.nextpos()
if 'DHT' in sen.sensors.keys():
    suw.add_widgetlabelvalue("DHTC", "{0:} DHT: ".format(S_THERMO),pos_sens, get_dht, 'c')
    pos_sens.nextpos()
    suw.add_widgetlabelvalue("DHTH", "{0:} DHT: ".format(S_HUMIDITY),pos_sens, get_dht, 'h')
    pos_sens.nextpos()
if 'HIH' in sen.sensors.keys():
    suw.add_widgetlabelvalue("HIHC", "{0:} HIH: ".format(S_THERMO),pos_sens, get_hih, 'c')
    pos_sens.nextpos()
    suw.add_widgetlabelvalue("HIHH", "{0:} HIH: ".format(S_HUMIDITY),pos_sens, get_hih, 'h')
    pos_sens.nextpos()
# could add more Sensors
if not NOMOON:
    suw.add_widgetlabelvalue("MOONIMAGE", "moon: ", pos_moon, getmoon)
    pos_moon.nextpos()
    suw.add_widgetlabelvalue("MOONPHASE", " / ", pos_moon, getphase)



def set_pwmreversed(index,value,selected):
    global pwmreversed
    #print("{0:} {1:}".format(value,selected))
    m = rpwm.getmode(index)
    if value == 0:
        m = PWMMode(m)&~PWMMode.reversed
    else:
        m = PWMMode(m)|PWMMode.reversed
    rpwm.setmode(index,m)

def update_datetime():
    scr.addstr(pos_datetime.y, pos_datetime.x, "{0:}".format(datetime.now().strftime('%Y-%m-%d  –  %H:%M:%S')))


suw.focus("PWM0")

counter = 0

def update():
    global counter
    scr.addstr(pos_status.y, pos_status.x,S_UPDATE)
    update_datetime()
    scr.refresh()
    for i in range(ROW1*ROW2):
        check_onoff(i)
    counter += 1
    if counter == K_UPDATE_COUNTER:
        get_dht('r')
        get_hih('r')    #read new values from sensors
        get_w1('r')
        counter = 0
    suw.update_all()
    scr.addstr(pos_status.y, pos_status.x,S_OK)
    scr.refresh()



def timed_update():
    update()
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

def save():
    configsave = suw.get_config()
    configsave['pwm'] = rpwm.get_config()

    with open(r'./config.yaml', 'w') as file:
        config = yaml.dump(configsave, file)

timed_update()
update()
key = ''
while key != ord('q'):
    key = scr.getch()
    suw.onkeyboard(key)
    if key == ord(' '):
        timed_update()
    if key == ord('t'):
        timed_update()
    if key == ord('r'):
        scr.clear();
        suw.rect(0, 0, 79, 40)
        update()
    if key == ord('s'):
        save()
    if key == ord('m'):
        if maintenance == False:
            setMaintenance()
        maintenance = not maintenance
        update()

save()
suw.quit()
lasttimer.cancel()
