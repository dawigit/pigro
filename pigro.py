# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#NOMOON = True
DRAWEDITCURSOR = True
NOAUTO = False
ROW1 = 4
ROW2 = 1
import sys

a_rere = False
a_nomoon = False
a_noinit = False
a_ccinit = 'default'
a_newconf = False
if len(sys.argv) > 1:
    for a in sys.argv:
        if a == '-rere':
            a_rere = True
        elif a == '-nomoon':
            a_nomoon = True
        elif a == '-noinit':
            a_noinit = True
        elif '-C' in a:
            a_ccinit = a[2:]
            if not a_ccinit in ['default','blue','red','c64','pip3boy']:
                a_ccinit = 'default'
        elif '-P' in a:
            setrow2 = a[2:]
            if setrow2.isdigit():
                setrow2 = int(setrow2)
            if setrow2 in range(1,5):
                ROW2 = setrow2
        elif a == '-newconf':
            a_newconf = True
        else:
            if a != 'pigro.py':
                print('unknown argument: '+a)


from base import *
import Adafruit_PCA9685
from pwm import PWM,PWMMode,PWM9685
import time
from datetime import datetime
import locale
import os
import yaml
import threading
from threading import Timer
from sensors import sen,W1,Sensor

rpwm = PWM9685(a_noinit)

con = Control()
numrules = 0
rulemode = False
rulename = None
seditrule = None
seditpos = 0
rulecursoroffset = 0
slsw = []
slo = []
slt = []

if len(sen.sensors) == 0:
    NOAUTO = True

if not a_nomoon:
    from moon import get_moon
    from moon import get_phase
    from moon import set_location
    def getmoon():
        return "{0:}".format(get_moon())
    def getphase():
        return "{0:3.2f}%".format(get_phase())
    city = "Munich"
    set_location(city)

from widget import *

os.environ['DE'] = 'EU/CET-1'
time.tzset()
dto=datetime.now()

K_UPDATE_COUNTER = 5 # sensors are read every 5th update
K_UPDATE_RCOUNTER = 1 # rules are applied every 5th update
K_AUTO_TEMP = 31
K_MAINTENANCE_LIGHT = 20    #pwm value for maintenance mode

#w = Widget(WPos(-1,-1),[WLabel('0')])
m = '🌞'


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
S_THERMO =   "🌡  "
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

S_TRILEFT = '◀'

L_PIGRO = "PiGro"


K_T1 = 1
K_T2 = 2
K_T3 = 3
K_T4 = 4

K_DHTH = 1
K_DHTT = 2

K_PWM_OUT = 15

truefalselist = ["False","True "]

DEV = True
UFREQ = 1
MAINTENANCETIME = 20
power_on = [False]*16
maintenance = [False]*16
maintenance_pwm = [20,0,0,0, 20,0,0,0, 20,0,0,0, 20,0,0,0]

lastmaintenance = [None]*16


pg = WPos(79,14*ROW2+3+22)
pos_pigro = WPos(6,2)
pos_status = WPos(2,2)
pos_datetime = WPos(53,1)
pos_moon = WPos(64,3)
pos_sens = WPos(44,8)
pos_maintenance = WPos(20,2)
pos_clock = WPos(13,11)

def wpwm_change(index,value,selected):
    global maintenance,maintenance_pwm
    if maintenance[index] is False:
        rpwm.set(index,value)
    else:
        rpwm.set(index,maintenance_pwm[index])

def check_onoff(port=0):
    global power_on,maintenance,maintenance_pwm
    t = datetime.now()
    c = suw.get_clock_time("CLOCK"+str(port)+"ON")
    ton = int(c.split(":")[0])*60+int(c.split(":")[1])
    c = suw.get_clock_time("CLOCK"+str(port)+"OFF")
    toff = int(c.split(":")[0])*60+int(c.split(":")[1])
    tnow = t.hour*60+t.minute
    if toff < ton:
        toff+=24*60
    if tnow >= ton and tnow <= toff:
        power_on[port] = True
        rpwm.enable(port)
        if maintenance[port] == False:
            suw._wlist['PWM'+str(port)].change_symbol('default')
            rpwm.set(port,int(suw._wlist["PWM"+str(port)].get_selected()*10))
        else:
            rpwm.set(port,maintenance_pwm[port])
    else:
        suw._wlist['PWM'+str(port)].change_symbol('off')
        power_on[port] = False
        rpwm.set(port,0)
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
            return str.format("{0:3.2f} %",sen.sensors['DHT'].value['h'])
        if m == 'c':
            return str.format("{0:3.2f} °C",sen.sensors['DHT'].value['c'])
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

def set_pwmreversed(index,value,selected=None):
    if value == 0:
        rpwm.submode(index,PWMMode.reversed)
    else:
        rpwm.addmode(index,PWMMode.reversed)
    #rpwm.changemode(index,m)


suw = SuWidget()
suw.select_colortheme(a_ccinit)
suwa = None
quit_suwa = False
suwer = None
quit_suwer = False
config = {}

try:
    file = open(r'./config.yaml', 'r')
    if file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        if a_rere :
            config['PWM0INV'] = 1
except:
    a_newconf = True

if a_newconf is True:
    config['pwm'] = rpwm.get_config()
    pwminv = [0,0,0,0]*ROW2  #eg. MeanWell Driver
    if a_rere :
        pwminv[0] = 1
    clkon = [[7,0],[0,0],[0,0],[0,0]]*ROW2
    clkoff = [[19,0],[0,0],[0,0],[23,59]]*ROW2
    for i in range(ROW1*ROW2):
        config['PWM'+str(i)] = 0
        config['CLOCK'+str(i)+'ON'] = clkon[i]
        config['CLOCK'+str(i)+'OFF'] = clkoff[i]
        config['PWM'+str(i)+'INV'] = pwminv[i]


suw.rect(0, 0, pg.x, pg.y)
suw.add_widgetlabel("PIGRO", L_PIGRO, pos_pigro)
p = WPos(6,4)
#leading symbols for PWMn
wsl = {'default':S_LAMP,'busy':S_WRENCH,'off':S_SLEEP}
wsf = {'default':S_FAN,'busy':S_WRENCH,'off':S_SLEEP}
wslist = [wsl,wsf,wsf,wsf]
slist = [S_LAMP,S_LAMP,S_FAN,S_FAN]
for j in range(ROW2):
    for i in range(ROW1):
        if i == 0:
            p.setnext(10,3)
        else:
            p.setnext(10,3)

        if i == 0:
            suw.add_widgetroller("PWM"+str(i+j*ROW1), Lpercent, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)],config['PWM'+str(i+j*ROW1)],0,1,
                [WSymbol(wslist[i],WPos(-4,1)), WLabel("PWM"+str(i+j*ROW1)+"-"+str(i+j*ROW1+3),WPos(0,-1))])
        else:
            suw.add_widgetroller("PWM"+str(i+j*ROW1), Lpercent, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)],config['PWM'+str(i+j*ROW1)],0,1,
                [WSymbol(wslist[i],WPos(-4,1))])
        p.nextposx()
        if i == 0 and j==0:
            suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"ON", p,
                config['CLOCK'+str(i+j*ROW1)+'ON'][0],config['CLOCK'+str(i+j*ROW1)+'ON'][1],
                [WLabel(" ⏰ ",WPos(-4,1)), WLabel("On/Off",WPos(0,-1))])
        else:
            suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"ON", p,
                config['CLOCK'+str(i+j*ROW1)+'ON'][0],config['CLOCK'+str(i+j*ROW1)+'ON'][1],
                [WLabel(" ⏰ ",WPos(-4,1))])
        p.nextposx()
        suw.add_widgetclock("CLOCK"+str(i+j*ROW1)+"OFF", p,
            config['CLOCK'+str(i+j*ROW1)+'OFF'][0],config['CLOCK'+str(i+j*ROW1)+'OFF'][1])
        p.nextposx()
        if i == 0 and j==0:
            suw.add_widgetroller("PWM"+str(i+j*ROW1)+"INV", truefalselist, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)+'INV'],config['PWM'+str(i+j*ROW1)+'INV'],0,1,
                [WLabel("Inverse",WPos(0,-1))])
        else:
            suw.add_widgetroller("PWM"+str(i+j*ROW1)+"INV", truefalselist, p, WMode.FNL,
                config['PWM'+str(i+j*ROW1)+'INV'],config['PWM'+str(i+j*ROW1)+'INV'],0,1)
        p.x = p.ix
        p.nextposy()
    p.setnext(0,2)
    p.nextpos()

if a_rere:
    rpwm.add(0,10,PWMMode.RERE,0,80)
else:
    rpwm.add(0,10,PWMMode.default,0,100)
rpwm.add(1,0,PWMMode.default,0,100)
for i in range(2,ROW1*ROW2):
    rpwm.add(i,0)
for i in range(ROW1*ROW2):
    rpwm.enable(i)
    suw.set_onchange("PWM"+str(i),wpwm_change,i)
    suw.set_onchange("PWM"+str(i)+"INV",set_pwmreversed,i)
    #suw.W("PWM"+str(i)).locked = maintenance[i]

pos_sens.setnext(0,1)
pos_moon.setnext(4,0)
#add_widgetlabelvalue(self, name, label, pos, getvalue=None, arg=None,p=None,s=None):
#p=prefix, s=suffix
if 'W10' in sen.sensors.keys():
    suw.add_widgetlabelvalue("W1T0", "{0:} W10: ".format(S_THERMO),pos_sens, get_w1, 0,"W10 "+S_THERMO)
    pos_sens.nextpos()
if 'W11' in sen.sensors.keys():
    suw.add_widgetlabelvalue("W1T1", "{0:} W11: ".format(S_THERMO),pos_sens, get_w1, 1,"W11 "+S_THERMO)
    pos_sens.nextpos()
if 'DHT' in sen.sensors.keys():
    suw.add_widgetlabelvalue("DHTC", "{0:} DHT: ".format(S_THERMO),pos_sens, get_dht, 'c',"DHT "+S_THERMO)
    pos_sens.nextpos()
    suw.add_widgetlabelvalue("DHTH", "{0:} DHT: ".format(S_HUMIDITY),pos_sens, get_dht, 'h',"DHT "+S_HUMIDITY)
    pos_sens.nextpos()
if 'HIH' in sen.sensors.keys():
    suw.add_widgetlabelvalue("HIHC", "{0:} HIH: ".format(S_THERMO),pos_sens, get_hih, 'c',"HIH "+S_THERMO)
    pos_sens.nextpos()
    suw.add_widgetlabelvalue("HIHH", "{0:} HIH: ".format(S_HUMIDITY),pos_sens, get_hih, 'h',"HIH "+S_HUMIDITY)
    pos_sens.nextpos()
# could add more Sensors
if not a_nomoon:
    suw.add_widgetlabelvalue("MOONIMAGE", " ", pos_moon, getmoon)
    pos_moon.nextpos()
    suw.add_widgetlabelvalue("MOONPHASE", " ", pos_moon, getphase,None,"/ ")

map = dict()
for i in range(ROW1*ROW2):
    map['PWM'+str(i)] = suw.W('PWM'+str(i))
for k in list(sen.sensors.keys()):
    if sen.sensors[k].valueisdict == True:
        for vk in sen.sensors[k].value.keys():
            map[k+'@'+vk] = sen.sensors[k]
    else:
        map[k] = sen.sensors[k]
# add to map so the strings can be evaled
#map['and'] = ' and '
#map['or'] = ' or '
if 'rules' in config:
    con.importrules(config['rules'],map)

def update_datetime():
        pos_datetime.draw("{0:}".format(datetime.now().strftime('%Y-%m-%d  –  %H:%M:%S')),curses.color_pair(CC[0]))

suw.focus("PWM0")
# counter for update -> apply rules/read sensors every n-th update
counter = 0
rcounter = 0

def update():
    global counter,rcounter
    pos_status.draw(S_UPDATE)
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

    rcounter += 1
    if rcounter == K_UPDATE_RCOUNTER:
        for k in list(con.rules.keys()):
            con.rid(k)
        rcounter = 0
    suw.update_all()
    pos_status.draw(S_OK)
    scr.refresh()

def timed_update():
    update()
    setClock()

def end_maintenance(i):
    global maintenance
    if type(i) is list:
        i = i[0]
    if maintenance[i] == True:
        maintenance[i] = False
        update()


def setClock():
    global lasttimer
    ti = Timer(UFREQ*60, timed_update)
    ti.start()
    lasttimer = ti

def setMaintenance(i):
    global lastmaintenance
    if lastmaintenance[i] is not None:
        lastmaintenance[i].cancel()
    tim = Timer(MAINTENANCETIME*60, end_maintenance,[i])
    tim.start()
    lastmaintenance[i] = tim

def save():
    configsave = suw.get_config()
    configsave['pwm'] = rpwm.get_config()
    configsave['rules'] = exportrules()
    with open(r'./config.yaml', 'w') as file:
        config = yaml.dump(configsave, file)

def strrule(k):
    dd = ''
    for r in k:
        if len(dd):
            dd+=' '
        if isinstance(r.value,Widget):
            dd+=r.value.name
        elif isinstance(r.value,Sensor):
            if r.index is not None:
                dd+=r.value.name+'@'+str(r.index)
            else:
                dd+=r.value.name
        elif type(r.value) is str:
            dd+=r.value
        else:
            dd+=str(r.value)
    return dd

def addrule(suwa,edit=None):
    global numrules,rulemode,seditrule,seditpos,slsw,slo,slt,rulename
    if edit is not None:
        rulename = edit
        seditrule = strrule(con.rules[edit])
        if seditpos is None:
            seditpos = seditrule.count(' ')

        con.edit_rule(rulename)
    else:
        seditrule = ''
        rulename = 'RULE'+str(len(list(con.rules.keys())))
        con.new_rule(rulename)
    #y, x = scr.getmaxyx()
    lp = WPos(2,1)
    suwa.add_widgetlabel('ARULE','',lp)
    p = WPos(1,2)
    p.setnext(12,0)

    sle = ['EXIT','INPUT',S_CLOCK,'->','DEL','ENTER']
    sls = list(sen.sensors.keys())
    slsw = list()
    slt = ['UP','DOWN','RAMP','ZIGZAG', 'RAB', 'ZZAB']
    for i in range(len(sls)):
        if sen.sensors[sls[i]].valueisdict:
            vkeys = list(sen.sensors[sls[i]].value.keys())
            for k in vkeys:
                slsw.append(sls[i]+'@'+k)
        else:
            slsw.append(sls[i])
    #slo = list(ops.keys())
    slo = ['<','>','=','(','+',')','/','<=','>=','!=','-','*','AND','OR']
    sld = list()
    for i in range(ROW1*ROW2):
        sld.append('PWM'+str(i))
    sl = [sle,slsw,slo,sld,slt]
    for i in range(len(sl)):
        suwa.add_widgetselect(rulename+'_'+str(i), sl[i], p, WMode.Frame)
        suwa.set_onchange(rulename+'_'+str(i), selectrule)
        p.nextpos()
    suwa.focus(rulename+'_'+str(0))
    suwa.touchwin()
    drawrule(seditpos,seditrule)


def drawrule(seditpos,seditrule):
    global rulecursoroffset
    wsadd(suwa.scr,1,3,suwa.spacer(70))
    if seditpos is not None:
        srs = seditrule.split(' ')
        s = ''
        sp = 0
        for i in range(len(srs)):
            v = srs[i]
            if i == seditpos:
                rulecursoroffset = sp + len(srs[i])+1
                if DRAWEDITCURSOR is True:
                    v+=S_TRILEFT
                else:
                    v+=' '
                wsadd(suwa.scr,1,3+sp,v,curses.A_BLINK | curses.A_BOLD | curses.A_REVERSE)
            else:
                v+= ' '
                wsadd(suwa.scr,1,3+sp,v)
            sp+=len(srs[i])+1
        if seditpos > seditrule.count(' ') or seditrule.count(' ') == 0:
            wsadd(suwa.scr,1,3+sp,S_TRILEFT,curses.A_BLINK)
    suwa.refresh()

def rinput(width):
    global rulemode,numrules,seditrule,seditpos,quit_suwa,slsw,slo,slt,rulename,rulecursoroffset
    value = suwa.input(rulecursoroffset+1,1,width,1,True)
    #else:
    #    value = suwa.input(5+len(seditrule)+1,1,width,1,True)
    return value

def selectrule(index,value,selected):
    global rulemode,numrules,seditrule,seditpos,quit_suwa,slsw,slo,slt,rulename
    if value == 'EXIT':
        quit_suwa = True
        return
    elif value == 'INPUT':
        #value = suwa.input(5+len(seditrule.split(S_TRILEFT)[0])+3,1,9,1,True)
        value = rinput(9)
        if len(value):
            if '.' in value:
                con.add_object(seditpos, value)
            if value.isdigit():
                con.add_object(seditpos, value)
        scr.refresh()
        suwa.update_all()
    elif value == S_CLOCK:
        tr = rinput(16)
#        tr = suwa.input(5+len(seditrule.split(S_TRILEFT)[0])+3,1,16,1,True)
        if '-' in tr:
            value = S_CLOCK+tr
        else:
            value = None
        if value is not None:
            con.add_object(seditpos, str(value))
        scr.refresh()
        suwa.update_all()
    elif value == 'DEL':
        if len(seditrule):
            if ' ' in seditrule:
                seditrule = seditrule.rsplit(' ', 1)[0]
            else:
                seditrule = ''
            con.del_last()
        value = None
    elif value == 'ENTER':
        if '->' in seditrule:
            con.add_rule()
            con.rid(rulename)
        quit_suwa = True
        return
    elif value in list(slsw):
        if '@' in value:
            vs = value.split('@')
            con.add_object(seditpos, sen.sensors[vs[0]],vs[1])
        else:
            con.add_object(seditpos, sen.sensors[value])
    elif value in ['->']:
        con.add_object(seditpos, value)
    elif value in list(slo):
        con.add_object(seditpos, value)
    elif value in slt:
        if value in ['RAB','ZZAB']:
            #tr = suwa.input(5+len(seditrule.split(S_TRILEFT)[0])+3,1,8,1,True)
            tr = rinput(8)
            if '-' in tr:
                value += tr
            else:
                value += '50-100'
        con.add_object(seditpos, str(value))
    elif 'PWM' in value:
        con.add_object(seditpos, suw.W(value))
    if value is not None:
        seditrule = strrule(con.editrule)
        seditpos += 1
    drawrule(seditpos,seditrule)


def addrule_exit():
    rulemode = False
    rw = list(suwa._wlist.keys())
    for w in rw:
        if 'RULE' in w:
            suwa.next()
            suwa.del_widget(w)
    rulename = None

def redraw():
    scr.clear();
    suw.rect(0, 0, pg.x, pg.y)
    update()

def edit_rule(arg,value,selected):
    global quit_suwer,seditrule,seditpos,rulename
    #quit_suwer = True
    if selected == 0:
        suwer_onoff()
        return
    seditrule = value
    seditpos = seditrule.count(' ')
    rulename = list(con.rules.keys())[selected-1]
    suwer_onoff()
    suwa_onoff()

def edit_rules(suwer):
    lp = WPos(1,1)
    d = ['QUIT']
    for k in list(con.rules.keys()):
        d.append(strrule(con.rules[k]))
    suwer.add_widgetselect('SUWER',d,lp,WMode.Frame)
    suwer.set_onchange('SUWER',edit_rule)
    suwer.focus('SUWER')
    suwer.touchwin()
    suwer.refresh()

def exportrules():
    x = []
    for rule in list(con.rules.keys()):
        rs = ''
        ru = con.rules[rule]
        for r in ru:
            if rs != '':
                rs += ' '
            if isinstance(r.value,ControlObject):
                n = r.value.name
                if r.index is not None:
                    n+='@'+r.index
                rs+=n
            elif isinstance(r.value,Widget):
                n = r.value.name
                rs+=n
            else:
                v = r.value
                rs += str(v)
        x.append(rs)
    return x


def suwa_onoff():
    global suwa,quit_suwa,rulename
    if quit_suwa is True:
        rulename = None
    if suwa is None:
        suwa = SuWidget(1,pg.y-23,76,21)
        suwa.frame()
        if rulename is not None:
            addrule(suwa,rulename)
        else:
            addrule(suwa)
    else:
        del suwa.scr
        del suwa
        suwa = None
        quit_suwa = False
        rulename = None
        suw.refresh()

def suwer_onoff():
    global suwer,quit_suwer
    if suwer is None:
        suwer = SuWidget(1,pg.y-23,76,21)
        suwer.frame()
        edit_rules(suwer)
    else:
        del suwer.scr
        del suwer
        suwer = None
        quit_suwer = False
        suw.refresh()


timed_update()
update()
key = ''
while key != ord('q'):
    if quit_suwa == True:
        suwa_onoff()
    if quit_suwer == True:
        suwer_onoff()

    key = scr.getch()
    if suwa is not None:
        suwa.onkeyboard(key)
        suwa.refresh()
    elif suwer is not None:
        suwer.onkeyboard(key)
        if suwer:
            suwer.refresh()
    else:
        suw.onkeyboard(key)
    if key == ord(' '):
        timed_update()
    if key == ord('t'):
        timed_update()
    if key == ord('r'):
        redraw()
    if key == ord('s'):
        save()
    for i in range(4):
        if key == ord(str(i+1)) and power_on[i]==True:
            if maintenance[i] == False:
                setMaintenance(i)
                suw._wlist['PWM'+str(i)].change_symbol('busy')
            else:
                suw._wlist['PWM'+str(i)].change_symbol('default')
            maintenance[i] = not maintenance[i]
            suw.W('PWM'+str(i)).locked = maintenance[i]
            update()
    if key == ord('a'):
        rulename = None
        seditrule = None
        seditpos = 0
        if suwer is None:
            suwa_onoff()
    if key == ord('>'):
        if seditrule is not None:
            if seditpos > seditrule.count(' ')+1:
                seditpos = seditrule.count(' ')
            if seditpos < seditrule.count(' ')+1:
                seditpos+=1
            drawrule(seditpos,seditrule)
    if key == ord('<'):
        if seditrule is not None:
            if seditpos > seditrule.count(' ')+1:
                seditpos = seditrule.count(' ')
            elif seditpos > 0:
                seditpos-=1
            drawrule(seditpos,seditrule)
    if key == ord('e'):
        if suwa is None:
            suwer_onoff()
    if key == ord('i'):
        try:
            file = open(r'./rules.yaml', 'r')
            if file:
                ir = yaml.load(file, Loader=yaml.FullLoader)
                con.importrules(ir, map)
        except:
            None
    if key == ord('x'):
        xr = exportrules()
        with open(r'./rules.yaml', 'w') as file:
            config = yaml.dump(xr, file)

save()
suw.quit()
lasttimer.cancel()
