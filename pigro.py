# -*- coding: utf-8 -*-
#!/usr/bin/env python3

NOMOON = True
NOAUTO = False

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
pos_maintenance = WPos(20,5)
pos_clock = WPos(13,11)

suw = SuWidget()

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
            pwmreversed = config['pwmreversed']
            if pwmreversed == True:
                exit()
            #config = yaml.dump(dict_file, file)
except:
    None

PWMFREQ = 10000
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(PWMFREQ)

def set_pwm(id,value):
    global power_on, maintenance,pwmreversed
    if type(value) == str:
        value = int(value)
    if id == 0 and power_on == False:
        value = 0
    if id == 0:
        if maintenance == True and power_on == True:
            value = K_MAINTENANCE_LIGHT
        if pwmreversed == True:
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

def update_onofflabel():
    global power_on
    return S_LAMP if power_on else S_SLEEP

def update_maintenance():
    global maintenance
    return S_WRENCH if maintenance else S_SPACE2

suw.rect(0, 0, 79, 32)
suw.add_widgetlabelvalue("PROMETHEUS", L_PIGROPRO, pos_pigropro, update_onofflabel)
suw.add_widgetlabelvalue("MAINTENANCE", L_MAINTENANCE, pos_pigropro, update_maintenance)
p = WPos(6,6)
slist = [S_LAMP,S_LAMP,S_FAN,S_FAN]
for i in range(4):
    if i == 0:
        p.setnext(10,3)
    else:
        p.setnext(10,2)

    p.set(6,6+(p.nexty*i))

    if i == 0:
        suw.add_widgetroller("PWM"+str(i), Lpercent, p, WMode.FNL,pwmlight,pwmlight,0,1,[slist[i],WPos(-4,1), "PWM"+str(i)+"-"+str(i+3),WPos(0,-1)])
    else:
        suw.add_widgetroller("PWM"+str(i), Lpercent, p, WMode.FNL,pwmlight,pwmlight,0,1,[slist[i],WPos(-4,1)])
    p.nextposx()
    if i == 0:
        suw.add_widgetclock("CLOCK"+str(i)+"ON", p, on_hour,on_minute,[" ⏰ ",WPos(-4,1), "On/Off",WPos(0,-1)])
    else:
        suw.add_widgetclock("CLOCK"+str(i)+"ON", p, on_hour,on_minute,[" ⏰ ",WPos(-4,1)])
    p.nextposx()
    suw.add_widgetclock("CLOCK"+str(i)+"OFF", p, off_hour,off_minute)
    p.nextposx()
    if i == 0:
        suw.add_widgetroller("PWM"+str(i)+"INV", truefalselist, p, WMode.FNL,pwmreversed,pwmreversed,0,1,["Inverse",WPos(0,-1)])
    else:
        suw.add_widgetroller("PWM"+str(i)+"INV", truefalselist, p, WMode.FNL,pwmreversed,pwmreversed,0,1)


def check_onoff():
    global power_on
    t = datetime.now()
    c = suw.get_clock_time("CLOCK0ON")
    if c is None:
        return
    ton = int(c.split(":")[0])*60+int(c.split(":")[1])
    c = suw.get_clock_time("CLOCK0OFF")
    if c is None:
        return
    toff = int(c.split(":")[0])*60+int(c.split(":")[1])
    tnow = t.hour*60+t.minute
    if toff < ton:
        toff+=24*60
#    suw.scr.addstr(0,0,"on: {0:} off: {1:} now: {2:} {3:}".format(ton,toff,tnow,type(ton)))
    if tnow >= ton and tnow <= toff:
        power_on = True
        set_pwm(0,int(suw._wlist["PWM0"].get_selected()*10))
    else:
        #power_on = False
        #set_pwm(0,0)
        power_on = True
        set_pwm(0,int(suw._wlist["PWM0"].get_selected()*10))


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


def set_pwmreversed(index,value,selected):
    global pwmreversed
    #print("{0:} {1:}".format(value,selected))
    if selected == 0:
        pwmreversed = False
    if selected == 1:
        pwmreversed = True



suw.set_onchange("PWM0",wpwm_change,0)
suw.set_onchange("PWM0INV", set_pwmreversed)

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

#vh = 10
#for i in range(1,16):
#    y = int(i/4)
#    x = int(i%4)
#    suw.add_widgetroller("PWM"+str(i), Lpercent, pos_pwm.x+(5*x), pos_pwm.y+(3*y),WMode.FNL,pwms[i],pwms[i])
#    suw.set_onchange("PWM"+str(i), wpwm_change, i)
#    set_pwm(i,pwmv[i])


def update_datetime():
    suw.scr.addstr(pos_datetime.y, pos_datetime.x, "{0:}".format(datetime.now().strftime('%Y-%m-%d  –  %H:%M:%S')))


suw.focus("PWM0")

counter = 0

def update():
    global counter
    suw.scr.addstr(pos_status.y, pos_status.x,S_UPDATE)
    update_datetime()
    suw.scr.refresh()
    counter += 1
    if counter == K_UPDATE_COUNTER:
        get_dht('r')
        get_hih('r')    #read new values from sensors
        get_w1('r')
        counter = 0
    suw.update_all()
    suw.scr.addstr(pos_status.y, pos_status.x,S_OK)
    suw.scr.refresh()



def timed_update():
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

def save():
    configsave = {'pwms' : pwms,
    'pwmv' : pwmv,
    'pwmlight' : suw._wlist["PWM0"].get_selected(),
    'on' : str(suw.get_clock_time("CLOCK0ON")),
    'off' : str(suw.get_clock_time("CLOCK0OFF")),
    'power' : power_on,
    'maintenance' : maintenance,
    'pwmreversed' : pwmreversed
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
    if key == ord('m'):
        if maintenance == False:
            setMaintenance()
        maintenance = not maintenance
        update()
        set_pwm(0,pwmv[0])
save()
suw.quit()
lasttimer.cancel()
