# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from enum import Flag, auto
import curses
from curses.textpad import rectangle
from base import BaseUtil
from collections import OrderedDict
S_CURSOR = "👉"
S_CLOCK = "⏰"
#scr = None
scr = curses.initscr()

class WMode(Flag):
    Default = auto()
    Frame = auto()
    NoCircle = auto()
    Live = auto()
    FNL = Frame | NoCircle | Live

class WPosAttr(Flag):
    top = auto()
    bottom = auto()
    left = auto()
    right = auto()

class WPos():
    def __init__(self, x, y):
         self.x = x
         self.y = y
         self.ix = x
         self.iy = y
    def set(self,x,y):
        self.x = x
        self.y = y
    def setnext(self,nextx,nexty):
        self.nextx = nextx
        self.nexty = nexty
    def nextpos(self):
        self.lastx = self.x
        self.lasty = self.y
        self.x += self.nextx
        self.y += self.nexty
    def nextposx(self):
        self.lastx = self.x
        self.x += self.nextx
    def nextposy(self):
        self.lasty = self.y
        self.y += self.nexty

class WValue():
    def __init__(self,value,getvalue=None,arg=None,prefix="",suffix=""):
        self.value = value
        self.getvalue = getvalue
        self.arg = arg
        self.prefix = prefix
        self.suffix = suffix

    def call_getvalue(self):
        if self.getvalue is not None:
            if callable(self.getvalue):
                if self.arg is None:
                    v = self.getvalue()
                else:
                    v = self.getvalue(self.arg)
                if self.prefix is not None:
                    v = self.prefix+str(v)
                if self.suffix is not None:
                    v = str(v)+self.suffix
                self.value = str(v)

class WLabel():
    def __init__(self,value,labelpos=None,wvalue=None):
        self.value = value
        self.labelpos = labelpos
        self.wvalue = wvalue
    def update(self):
        if self.wvalue:
            self.wvalue.call_getvalue()
            self.value = self.wvalue.value

            def get(self):
                self.update()
                return self.value
class WSymbol():
    def __init__(self,wsmap,labelpos):
        if wsmap is None:
            wsmap = {'default':''}
        self.value = wsmap['default']
        self.mapvalue = 'default'
        self.labelpos = labelpos
        self.wsmap = wsmap

    def change(self,name):
        self.value = self.wsmap[name]
        self.mapvalue = name

    def is_default(self):
        if self.value == self.wsmap['default']:
            return True
        else:
            return False
    def is_symbol(self,s):
        return self.value == s
    def is_mapvalue(self,mapvalue):
        return self.mapvalue == mapvalue
    def get(self):
        return self.value
    def getmapvalue(self):
        return self.mapvalue

def init():
    y, x = scr.getmaxyx()
    scr.clear()
    curses.resizeterm(y, x)
    scr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.savetty()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLUE)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    scr.keypad(1)
    ccolor = curses.color_pair(0)
    return scr

def rect(x,y,w,h):
    global scr
    rectangle(scr,y,x,y+h,x+w)

def sadd(y,x,v,w=0):
    global scr
    scr.addstr(y,x,v,w)

h24 = []
h24us = []
m60 = []
percent = []

for i in range(24):
    h24.append(str(i).zfill(2))
for i in range(60):
    m60.append(str(i).zfill(2))
for i in range(11):
    percent.append('{:>3}'.format(str(i*10)))

class BaseWidget(BaseUtil):
    def __init__(self):
        None

class Widget(BaseWidget):
    def __init__(self,pos,labels=None):
        super().__init__()
        self.pos = pos
        self.onunfocus = None
        self.onchange = None
        self.focused = False
        self.nofocus = False
        self.haslabels = False
        self.labels = list()
        if labels is not None:
            self.haslabels = True
        if type(labels) is str:
            self.add_label(labels,WPos(0,0))
        elif type(labels) is WLabel:
            self.labels.append(labels)
        elif type(labels) is WSymbol:
            self.labels.append(labels)
        elif type(labels) is list:
            self.labels = labels

    def focus(self):
        self.focused = True

    def unfocus(self):
        self.focused = False
        if self.onunfocus:
            self.onunfocus()

    def set_onunfocus(self,onunfocus):
        self.onunfocus = onunfocus

    def set_onchange(self,onchange,arg=None):
        self.onchange = onchange
        self.arg = arg

    def is_focus(self):
        return self.focused

    def add_label(self,label,labelpos):
        self.labels.append(WLabel(label,labelpos))
        self.haslabels = True

    def change_label(self,index,label):
        if self.haslabels and len(self.labels) > index and index>0:
            self.labels[index].label = label

    def change_symbol(self,name):
        self.labels[0].change(name)
        self.draw()
    def is_defaultsymbol(self):
        return self.labels[0].is_default()
    def is_symbol(self,s):
        return self.labels[0].get() == s
    def is_mapvalue(self,mapvalue):
        return self.labels[0].mapvalue == mapvalue
    def getmapvalue(self):
        return self.labels[0].mapvalue

    def draw(self):
        self.draw_labels()

    def draw_labels(self):
        for l in self.labels:
            if type(l) is WLabel:
                if l.wvalue is not None:
                    l.update()
            sadd(self.pos.y+l.labelpos.y, self.pos.x+l.labelpos.x, l.value)
    def onkeyboard(self,key):
        None
    def getconfig(self):
        None


class WidgetRoller(Widget):
    def __init__(self, data, pos,attributes=WMode.Frame,selected=0,cursorposition=0,w=0,h=1,labels=None):
        super().__init__(pos,labels)
        self.attributes = attributes
        if w == 0:
            for d in data:
                if len(d) > w:
                    w = len(d)
        self.w = w
        self.h = h
        self.data = data
        if type(selected) is str:
            selected = str(selected)
        self.selected = selected
        self.cursorposition = cursorposition
        self.ccolor = curses.color_pair(0)

    def focus(self):
        super().focus()

    def unfocus(self):
        super().unfocus()
        self.draw()

    def is_focus(self):
        return super().is_focus()

    def draw(self):
        super().draw()
        plusone = 1
        if WMode.Frame in WMode(self.attributes):
            rect(self.pos.x,self.pos.y,self.w+1,self.h+1)
        else:
            plusone = 0
        cc = None
        cs = None
        if self.is_focus():
            cc = curses.color_pair(4)
            cs = curses.color_pair(6)
        else:
            cc = curses.color_pair(0)
            cs = curses.color_pair(5)
        self.ccolor = cc
        for i in range(self.h):
            if self.cursorposition == self.selected:
                self.ccolor = cs
            sadd(self.pos.y + i + plusone, self.pos.x + plusone, self.data[self.cursorposition],self.ccolor)

    def select(self):
        self.selected = self.cursorposition
        self.draw()
        if callable(self.onchange):
            self.onchange(self.arg,self.data[self.selected],self.selected)

    def movecursor(self,direction):
        if type(direction) is str:
            direction = int(direction)
        if WMode.NoCircle in WMode(self.attributes):
            if self.cursorposition+direction < 0 or self.cursorposition+direction > len(self.data)-1:
                return
        self.cursorposition += direction
        if self.cursorposition < 0:
            self.cursorposition = len(self.data)-1
        if self.cursorposition > len(self.data)-1:
            self.cursorposition = 0
        if WMode.Live in WMode(self.attributes):
            self.select()
        self.draw()

    def onkeyboard(self,key):
        if key == ord('d'):
            self.draw()
        if key == curses.KEY_UP:
            self.movecursor(1)
        if key == curses.KEY_DOWN:
            self.movecursor(-1)
        if key == ord('\n') or key == ord(' '):
            self.select()


    def get_selected(self):
        return self.selected

    def set_selected(self,selected):
        self.selected = selected

    def get_selected_value(self):
        return self.data[self.selected]

    def getconfig(self):
        return self.get_selected()


class WidgetSelect(Widget):
    global scr
    def __init__(self, data, pos,attributes=0,selected=0,cursorposition=0,w=0,h=0, margin=3,labels=None):
        super().__init__(pos,labels)
        #self.id = id
        if selected >= len(data):
            raise ValueError('selected value does not exist in data')
        self.attributes = attributes
        if w == 0:
            for d in data:
                if len(d) > w:
                    w = len(d)
        if h == 0:
            h = len(data)
        self.w = w
        self.h = h
        self.data = data
        self.selected = selected
        self.cursorposition = int(cursorposition)
        self.margin = margin
        self.ccolor = curses.color_pair(0)

        self.draw()

    def focus(self):
        super().focus()
        self.drawcursor()

    def unfocus(self):
        super().unfocus()
        self.removecursor()

    def is_focus(self):
        return super().is_focus()

    def draw(self):
        global scr
        super().draw()
        rect(self.pos.x,self.pos.y,self.w+self.margin+2,self.h+1)
        row = 0
        for i in self.data:
            if row > self.h - 1:
                sadd(self.pos.y + 1 + row, self.pos.x + 1 + self.margin, self.spacer(self.w+self.margin),self.ccolor)
                continue
            if row == self.selected:
                self.ccolor = curses.color_pair(6)
            sadd(self.pos.y + 1 + row, self.pos.x + 1 + self.margin, self.data[row],self.ccolor)
            self.ccolor = curses.color_pair(0)
            row += 1
        if self.is_focus() == True:
            self.drawcursor()

    def drawcursor(self):
        global scr
        sadd(self.pos.y + 1 + self.cursorposition,self.pos.x + 1,S_CURSOR,self.ccolor)

    def movecursor(self,direction):
        global scr
        sadd(self.pos.y + 1 + self.cursorposition, self.pos.x + 1, self.spacer(self.margin),self.ccolor)
        if direction == 1 and self.cursorposition+1 < len(self.data):
            self.cursorposition += 1
        if direction == -1 and self.cursorposition > 0:
            self.cursorposition -= 1
        if WMode.Live in WMode(self.attributes):
            self.select()
        self.drawcursor()

    def removecursor(self):
        global scr
        sadd(self.pos.y + 1 + self.cursorposition, self.pos.x + 1, self.spacer(self.margin),self.ccolor)

    def select(self):
        self.selected = self.cursorposition
        self.cleardraw()
        self.draw()
        if callable(self.onchange):
            self.onchange(self.arg,self.data[self.selected],self.selected)

    def onkeyboard(self,key):
        if key == ord('d'):
            self.draw()
        if key == curses.KEY_UP:
            self.movecursor(-1)
        if key == curses.KEY_DOWN:
            self.movecursor(1)
        if key == ord('\n') or key == ord(' '):
            self.select()

    def spacer(self,spaces):
        sp = ""
        for i in range(spaces):
            sp+=" "
        return sp

    def cleardraw(self):
        for y in range(self.h + 1):
            sadd(self.pos.y + y, self.pos.x, self.spacer(self.w + 1),self.ccolor)

    def get_selected(self):
        return self.selected

    def get_selected_value(self):
        return self.data[self.selected]

    def getconfig(self):
        return self.get_selected()

class WidgetClock(Widget):
    def __init__(self, pos, time, labels=None):
        super().__init__(pos, labels)
        self.nofocus = True
        p1 = WPos(pos.x+1,pos.y+1)
        p2 = WPos(pos.x+4,pos.y+1)
        self.hour = WidgetRoller(h24,p1,WMode.Default,int(time.split(":")[0]),int(time.split(":")[0]))
        self.minute = WidgetRoller(m60,p2,WMode.Default,int(time.split(":")[1]),int(time.split(":")[1]))
        self.draw()

    def draw(self):
        global scr
        super().draw()
        rect(self.pos.x,self.pos.y,6,2)
        self.hour.draw()
        sadd(self.pos.y+1,self.pos.x+3,":")
        self.minute.draw()

    def set(self,time):
        self.hour.select(int(time.split(":")[0]))
        self.minute.select(int(time.split(":")[1]))
    def get(self):
        return self.hour.get_selected_value()+":"+self.minute.get_selected_value()
    def getconfig(self):
        return [self.hour.get_selected(),self.minute.get_selected()]


class SuWidget():
    global scr
    global rect
    _wlist = OrderedDict()
    _focus = ""
    def __init__(self):
        self.scr = init()
        self.rect = rect

    def set_onchange(self,name,onchange,arg=None):
        SuWidget._wlist[name].set_onchange(onchange,arg)

    def add_widgetselect(self, name, data, pos,attributes=0, selected=0, cursorposition=0, w=0,h=0, margin=3,labels=None):
        SuWidget._wlist[name] = WidgetSelect(data,WPos(pos.x,pos.y),attributes,selected,cursorposition,w,h,margin,labels)
        self._focus = name

    def add_widgetroller(self, name, data, pos, attributes=WMode.Frame, selected=0, cursorposition=0, w=0,h=1,labels=None):
        SuWidget._wlist[name] = WidgetRoller(data,WPos(pos.x,pos.y),attributes,selected,cursorposition,w,h,labels)
        self._focus = name

    def add_widgetlabel(self, name, label, pos):
        x = pos.x
        y = pos.y
        SuWidget._wlist[name] = Widget(WPos(x,y),label)

    def add_widgetlabelvalue(self, name, label, pos, getvalue=None, arg=None,p=None,s=None):
        x = pos.x
        y = pos.y
        SuWidget._wlist[name] = Widget(WPos(x,y),[WLabel(label,WPos(0,0),WValue(label,getvalue,arg,p,s))])

    def add_widgetclock(self,name,pos,hours,minutes,labels=None):
        SuWidget._wlist[name] = WidgetClock(WPos(pos.x,pos.y),str(hours)+":"+str(minutes),labels)
        SuWidget._wlist[name+"0"] = SuWidget._wlist[name].hour
        SuWidget._wlist[name+"1"] = SuWidget._wlist[name].minute

    def get_clock_time(self,name):
        return SuWidget._wlist[name].get()

    def next(self):
        SuWidget._wlist[SuWidget._focus].unfocus()
        k = list(SuWidget._wlist.keys())
        if k.index(SuWidget._focus) < len(k)-1:
            SuWidget._focus = k[k.index(SuWidget._focus)+1]
        else:
            SuWidget._focus = k[0]
        if SuWidget._wlist[SuWidget._focus].nofocus == True:
            self.next()
        SuWidget._wlist[SuWidget._focus].focus()
        SuWidget._wlist[SuWidget._focus].draw()

    def prev(self):
        SuWidget._wlist[SuWidget._focus].unfocus()
        k = list(SuWidget._wlist.keys())
        if k.index(SuWidget._focus) == 0:
            SuWidget._focus = k[len(k)-1]
        else:
            SuWidget._focus = k[k.index(SuWidget._focus)-1]
        if SuWidget._wlist[SuWidget._focus].nofocus == True:
            self.prev()
        SuWidget._wlist[SuWidget._focus].focus()
        SuWidget._wlist[SuWidget._focus].draw()

    def focus(self,name):
        if name in SuWidget._wlist.keys():
            SuWidget._focus = name
        SuWidget._wlist[SuWidget._focus].focus()
        SuWidget._wlist[SuWidget._focus].draw()

    def update(self,name):
        SuWidget._wlist[name].draw()

    def onkeyboard(self,key):
        if key == curses.KEY_RIGHT:
            self.next()
        if key == curses.KEY_LEFT:
            self.prev()
        SuWidget._wlist[SuWidget._focus].onkeyboard(key)

    def quit(self):
        curses.nocbreak()
        scr.keypad(False)
        curses.resetty()
        curses.endwin()
        curses.curs_set(1)
        curses.echo(True)

    def update_all(self):
        for key in SuWidget._wlist.keys():
            SuWidget._wlist[key].draw()

    def get_config(self):
        conf = {}
        for key in SuWidget._wlist.keys():
            conf[key] = SuWidget._wlist[key].getconfig()
        return conf
