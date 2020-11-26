# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from enum import Flag, auto
import curses
from curses.textpad import rectangle,Textbox
from base import OpList
from collections import OrderedDict
S_CURSOR = "👉"
S_CLOCK = "⏰"
#scr = None
scr = curses.initscr()

CCdefault = [0,1,2,3,4,5,6,7]
CCpip3boy = [3,1,2,7,7,7,3,7]
CCred = [8,1,2,10,4,10,13,7]
CCblue = [11,1,2,3,11,11,12,7]
CCc64 = [5,1,2,3,12,5,6,7]
CThemes = {
    'default': CCdefault,
    'pip3boy': CCpip3boy,
    'red': CCred,
    'blue': CCblue,
    'c64': CCc64,
}

CC = CCdefault

class WMode(Flag):
    Default = auto()
    Frame = auto()
    NoCircle = auto()
    Live = auto()
    NoFocus = auto()
    FNL = Frame | NoCircle | Live

class WPosAttr(Flag):
    top = auto()
    bottom = auto()
    left = auto()
    right = auto()

class WPos():
    def __init__(self, x, y, win = None):
         self.x = x
         self.y = y
         self.ix = x
         self.iy = y
         self.win = win
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
    def draw(self,value,c=None):
        if c is None:
            c = CC[0]
        if self.win is not None:
            self.win.addstr(self.y,self.x,value,c)
        else:
            scr.addstr(self.y,self.x,value,c)
    def cloneplus(self,x,y):
        return WPos(self.x+x,self.y+y)
    def __add__(self,other):
        self.x += other.x
        self.y += other.y

class WEPos(WPos):
    def __init__(self, x, y,w=0,h=0,win=None):
        super().__init__(x,y,win)
        self.w = w
        self.h = h

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
        if labelpos is None:
            labelpos = WPos(0,0)
        self.labelpos = labelpos
        self.wvalue = wvalue
        self.ccolor = curses.color_pair(CC[0])
    def update(self):
        if self.wvalue is not None:
            self.wvalue.call_getvalue()
            self.value = self.wvalue.value

    def get(self):
        self.update()
        return self.value

    def set_color(self,color):
        self.ccolor = curses.color_pair(color)

class WSymbol():
    def __init__(self,wsmap,labelpos):
        if wsmap is None:
            wsmap = {'default':''}
        self.value = wsmap['default']
        self.mapvalue = 'default'
        self.labelpos = labelpos
        self.wsmap = wsmap
        self.ccolor = ccp(0)

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

def curinit():
    y, x = scr.getmaxyx()
    scr.clear()
    curses.resizeterm(y, x)
    scr.refresh()
    scr.keypad(True)
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
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(10, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(12, curses.COLOR_BLUE, curses.COLOR_CYAN)
    curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    scr.keypad(1)
    curses.pair_content
    scr.bkgd(' ', curses.color_pair(6))
    ccolor = curses.color_pair(CC[0])
    return scr

def ccp(i):
    return curses.color_pair(i)

def rect(x,y,w,h):
    global scr
    rectangle(scr,y,x,y+h,x+w)

def wrect(win,x,y,w,h,c):
    #rectangle(win,y,x,y+h,x+w)
    xrect(win,y,x,y+h,x+w,c)

def xrect(win, uly, ulx, lry, lrx, cc):
    """Draw a rectangle with corners at the provided upper-left
    and lower-right coordinates.
    └┌┘┐─│
    """
    wvline(win, uly+1, ulx, '│', lry - uly - 1, cc)
    whline(win, uly, ulx+1, '─', lrx - ulx - 1, cc)
    whline(win, lry, ulx+1, '─', lrx - ulx - 1, cc)
    wvline(win, uly+1, lrx, '│', lry - uly - 1, cc)
    win.addstr(uly, ulx, '┌' , cc)
    win.addstr(uly, lrx, '┐' , cc)
    win.addstr(lry, lrx, '┘', cc)
    win.addstr(lry, ulx, '└', cc)

def wvline(win,y,x,c,l,cc):
    for i in range(l):
        win.addstr(y+i,x,c,cc)

def whline(win,y,x,c,l,cc):
    for i in range(l):
        win.addstr(y,x+i,c,cc)


def sadd(y,x,s,attr=0):
    global scr
    scr.addstr(y,x,s,attr)
def wsadd(win,y,x,s,attr=0):
    win.addstr(y,x,s,attr)

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

class BaseWidget():
    def __init__(self,win):
        self.win = win

class Widget(BaseWidget):
    def __init__(self,win,name,pos,labels=None,attributes=WMode.NoFocus):
        super().__init__(win)
        self.name = name
        self.pos = pos
        self.attributes = attributes
        self.onunfocus = None
        self.onchange = None
        self.focused = False
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
        self.locked = False
        self.ccolor = curses.color_pair(CC[0])
        self.onfocus = None

    def focus(self):
        self.focused = True
        if callable(self.onfocus):
            self.onfocus()

    def unfocus(self):
        self.focused = False
        if self.onunfocus:
            self.onunfocus()

    def set_onunfocus(self,onunfocus):
        self.onunfocus = onunfocus

    def set_onfocus(self,onfocus):
        self.onfocus = onfocus

    def set_onchange(self,onchange,arg=None):
        self.onchange = onchange
        self.arg = arg

    def is_focus(self):
        return self.focused

    def add_label(self,label,labelpos):
        self.labels.append(WLabel(label,labelpos))
        self.haslabels = True

    def change_label(self,index,label):
        if self.haslabels and len(self.labels) > index: #and index>0
            self.labels[index].label = label
        self.draw()

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
        first = True
        for l in self.labels:
            if type(l) is WLabel:
                if l.wvalue is not None:
                    l.update()
            wsadd(self.win,self.pos.y+l.labelpos.y, self.pos.x+l.labelpos.x, l.value, ccp(0) if isinstance(l.value, WSymbol) else l.ccolor)
            first = False
    def onkeyboard(self,key,altkey):
        None
    def getconfig(self):
        None




class WidgetRoller(Widget):
    def __init__(self, win,name, data, pos,attributes=WMode.Frame,selected=0,cursorposition=0,w=0,h=1,labels=None):
        super().__init__(win,name,pos,labels)
        self.attributes = attributes
        if w == 0:
            for d in data:
                if len(d) > w:
                    w = len(d)
        self.w = w
        self.h = h
        self.data = data
        self.selected = int(selected)
        self.cursorposition = int(cursorposition)
        self.ccolor = curses.color_pair(CC[0])

    def focus(self):
        super().focus()

    def unfocus(self):
        super().unfocus()
        self.draw()

    def is_focus(self):
        return super().is_focus()

    def draw(self):
        super().draw()
        cc = None
        cs = None
        if self.is_focus():
            cc = curses.color_pair(CC[4])
            cs = curses.color_pair(CC[6])
        else:
            cc = curses.color_pair(CC[0])
            cs = curses.color_pair(CC[5])
        self.ccolor = cc
        plusone = 1
        if WMode.Frame in WMode(self.attributes):
            wrect(self.win,self.pos.x,self.pos.y,self.w+1,self.h+1,cc)
        else:
            plusone = 0
        for i in range(self.h):
            if self.cursorposition == self.selected:
                self.ccolor = cs
            wsadd(self.win,self.pos.y + i + plusone, self.pos.x + plusone, self.data[self.cursorposition],self.ccolor)

    def select(self):
        self.selected = self.cursorposition
        self.draw()
        if callable(self.onchange):
            self.onchange(self.arg,self.data[self.selected],self.selected)

    def movecursor(self,direction):
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

    def up(self):
            if self.locked is False:
                self.movecursor(1)

    def down(self):
            if self.locked is False:
                self.movecursor(-1)

    def set(self,index):
            if self.locked is False:
                self.cursorposition = int(index)
                self.select()
                self.win.refresh()

    def onkeyboard(self,key,altkey):
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

    def get_selected_value(self):
        return self.data[self.selected]

    def getconfig(self):
        return self.get_selected()


class WidgetSelect(Widget):
    global scr
    def __init__(self, win, name, data, pos,attributes=0,selected=0,cursorposition=0,w=0,h=0, margin=3,labels=None):
        super().__init__(win,name,pos,labels)
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
        self.selected = int(selected)
        self.cursorposition = int(cursorposition)
        self.margin = margin
        self.ccolor = curses.color_pair(CC[0])

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
        wrect(self.win, self.pos.x,self.pos.y,self.w+self.margin+2,self.h+1,self.ccolor)
        row = 0
        for i in self.data:
            if row > self.h - 1:
                wsadd(self.win, self.pos.y + 1 + row, self.pos.x + 1 + self.margin, self.spacer(self.w+self.margin),self.ccolor)
                continue
            if row == self.selected:
                self.ccolor = curses.color_pair(CC[6])
            wsadd(self.win, self.pos.y + 1 + row, self.pos.x + 1 + self.margin, self.data[row],self.ccolor)
            self.ccolor = curses.color_pair(CC[0])
            row += 1
        if self.is_focus() == True:
            self.drawcursor()
        self.win.refresh()

    def drawcursor(self):
        global scr
        wsadd(self.win, self.pos.y + 1 + self.cursorposition,self.pos.x + 1,S_CURSOR,self.ccolor)

    def movecursor(self,direction):
        global scr
        direction = int(direction)
        wsadd(self.win, self.pos.y + 1 + self.cursorposition, self.pos.x + 1, self.spacer(self.margin),self.ccolor)
        if direction == 1 and self.cursorposition+1 < len(self.data):
            self.cursorposition += 1
        if direction == -1 and self.cursorposition > 0:
            self.cursorposition -= 1
        if WMode.Live in WMode(self.attributes):
            self.select()
        self.drawcursor()

    def removecursor(self):
        global scr
        wsadd(self.win, self.pos.y + 1 + self.cursorposition, self.pos.x + 1, self.spacer(self.margin),self.ccolor)

    def select(self):
        self.selected = self.cursorposition
        self.cleardraw()
        self.draw()
        if callable(self.onchange):
            self.onchange(self.arg,self.data[self.selected],self.selected)

    def up(self):
        if self.locked is False:
            self.movecursor(1)

    def down(self):
        if self.locked is False:
            self.movecursor(-1)

    def set(self,index):
            if self.locked is False:
                self.cursorposition = int(index)
                self.select()
                #self.draw()
                self.win.refresh()
                #self.movecursor(0)


    def onkeyboard(self,key,altkey):
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
        for y in range(self.h-1):
            wsadd(self.win, self.pos.y + y, self.pos.x, self.spacer(self.w + 1),self.ccolor)

    def get_selected(self):
        return self.selected
    def set_selected(self,selected):
        self.selected = int(selected)

    def get_selected_value(self):
        return self.data[self.selected]

    def getconfig(self):
        return self.get_selected()

class WidgetClock(Widget):
    def __init__(self, win, name, pos, time, labels=None):
        super().__init__(win, name, pos, labels)
        p1 = WPos(pos.x+1,pos.y+1)
        p2 = WPos(pos.x+4,pos.y+1)
        self.hour = WidgetRoller(win,name+'h',h24,p1,WMode.Default,int(time.split(":")[0]),int(time.split(":")[0]))
        self.minute = WidgetRoller(win,name+'m',m60,p2,WMode.Default,int(time.split(":")[1]),int(time.split(":")[1]))
        self.ccolor = curses.color_pair(CC[0])
        self.draw()
        self.hour.set_onunfocus(self.draw)
        self.minute.set_onunfocus(self.draw)
        self.set_onunfocus(self.draw)
        self.hour.set_onfocus(self.draw)
        self.minute.set_onfocus(self.draw)
        self.set_onfocus(self.draw)

    def focus(self):
        super().focus()

    def unfocus(self):
        super().unfocus()

    def is_focus(self):
        return self.focused or self.hour.is_focus() or self.minute.is_focus()

    def draw(self):
        super().draw()
        if self.is_focus():
            self.ccolor = curses.color_pair(CC[4])
        else:
            self.ccolor = curses.color_pair(CC[0])

        wrect(self.win, self.pos.x,self.pos.y,6,2,self.ccolor)
        self.hour.draw()
        wsadd(self.win, self.pos.y+1,self.pos.x+3,":",self.ccolor)
        self.minute.draw()

    def set_time(self,time):
        self.hour.set(int(time.split(":")[0]))
        self.minute.set(int(time.split(":")[1]))
    def get_timestr(self):
        return self.hour.get_selected_value()+":"+self.minute.get_selected_value()
    def getconfig(self):
        return [self.hour.get_selected(),self.minute.get_selected()]


class SuWidget():
    def __init__(self,x=None,y=None,w=None,h=None):
        if x is not None:
            self.scr = self.new_win(x,y,w,h)
            self.x = x
            self.y = y
        else:
            self.scr = curinit()
            self.x = 0
            self.y = 0
            self.scr.bkgd(' ', ccp(CC[0]))

        self.wrect = wrect
        self.w = w
        self.h = h
        self.framed = False

        self._wlist = OrderedDict()
        self._focus = ""

    def W(self,name):
        return self._wlist[name]

    def set_onchange(self,name,onchange,arg=None):
        self._wlist[name].set_onchange(onchange,arg)

    def new_win(self,x,y,w,h):
        nw = curses.newwin(h,w,y,x)
        nw.bkgd(' ', curses.color_pair(CC[0]))
        return nw

    #def add_widgetwin(self,name,pos,w,h):
    #    self._wlist[name] = WidgetWin(name,pos,w,h)

    def add_widgetselect(self, name, data, pos,attributes=0, selected=0, cursorposition=0, w=0,h=0, margin=3,labels=None):
        self._wlist[name] = WidgetSelect(self.scr, name, data,WPos(pos.x,pos.y),attributes,selected,cursorposition,w,h,margin,labels)
        self._focus = name

    def add_widgetroller(self, name, data, pos, attributes=WMode.Frame, selected=0, cursorposition=0, w=0,h=1,labels=None):
        self._wlist[name] = WidgetRoller(self.scr, name, data,WPos(pos.x,pos.y),attributes,selected,cursorposition,w,h,labels)
        self._focus = name

    def add_widgetlabel(self, name, label, pos):
        x = pos.x
        y = pos.y
        self._wlist[name] = Widget(self.scr, name, WPos(x,y),label)

    def add_widgetlabelvalue(self, name, label, pos, getvalue=None, arg=None,p=None,s=None):
        x = pos.x
        y = pos.y
        self._wlist[name] = Widget(self.scr, name, WPos(x,y),[WLabel(label,WPos(0,0),WValue(label,getvalue,arg,p,s))])

    def add_widgetclock(self,name,pos,hours,minutes,labels=None):
        self._wlist[name] = WidgetClock(self.scr, name, WPos(pos.x,pos.y),str(hours)+":"+str(minutes),labels)
        self._wlist[name+"0"] = self._wlist[name].hour
        self._wlist[name+"1"] = self._wlist[name].minute

    def del_widget(self,name):
        del (self._wlist[name])

    def move_widget(self,name,win):
        win.widgets[name] = self._wlist[name]
        del self._wlist[name]
    #def w(self,name):
    #    return self._wlist[name]

    def get_clock_time(self,name):
        return self._wlist[name].get_timestr()

    def next(self):
        self._wlist[self._focus].unfocus()
        k = list(self._wlist.keys())
        if k.index(self._focus) < len(k)-1:
            self._focus = k[k.index(self._focus)+1]
        else:
            self._focus = k[0]
        if self._wlist[self._focus].attributes&WMode.NoFocus:
            self._wlist[self._focus].focus()
            self._wlist[self._focus].draw()
            self.next()
        self._wlist[self._focus].focus()
        self._wlist[self._focus].draw()

    def prev(self):
        self._wlist[self._focus].unfocus()
        k = list(self._wlist.keys())
        if k.index(self._focus) == 0:
            self._focus = k[len(k)-1]
        else:
            self._focus = k[k.index(self._focus)-1]
        if self._wlist[self._focus].attributes & WMode.NoFocus:
            self._wlist[self._focus].focus()
            self._wlist[self._focus].draw()
            self.prev()
        self._wlist[self._focus].focus()
        self._wlist[self._focus].draw()

    def focus(self,name):
        if name in self._wlist.keys():
            self._focus = name
        self._wlist[self._focus].focus()
        self._wlist[self._focus].draw()

    def update(self,name):
        self._wlist[name].draw()

    def onkeyboard(self,key,altkey):
        if key == curses.KEY_RIGHT:
            self.next()
        if key == curses.KEY_LEFT:
            self.prev()
        self._wlist[self._focus].onkeyboard(key,altkey)

    def quit(self):
        curses.nocbreak()
        scr.keypad(False)
        curses.echo()
        curses.endwin()


    def update_all(self):
        for key in self._wlist.keys():
            self._wlist[key].draw()
        if self.framed is True:
            self.frame()

    def get_config(self):
        conf = {}
        for key in self._wlist.keys():
            conf[key] = self._wlist[key].getconfig()
        return conf

    def spacer(self,spaces):
        sp = ""
        for i in range(spaces):
            sp+=" "
        return sp

    def show(self):
        self.hidden = False
    def hide(self):
        self.hiden = True

    def refresh(self):
        self.scr.touchwin()
        self.scr.refresh()
    def touchwin(self):
        self.scr.touchwin()
    def cleardraw(self,x,y,w,h):
        for ay in range(h-2):
            sadd(y + ay, x, self.spacer(w))
    def wcleardraw(self,win,x,y,w,h):
        for ay in range(h-2):
            wsadd(win, y + ay, x, self.spacer(w))
    def frame(self):
        wrect(self.scr,0,0,self.w-2,self.h-1,ccp(CC[0]))
        self.framed = True

    def input(self,x,y,w,h,frame=False):
        f = 0
        pi = WPos(x,y)
        win = curses.newwin(h, w, self.y+pi.y, self.x+pi.x)
        if frame is True:
            wrect(self.scr,pi.x-1,pi.y-1,w+1,h+1,ccp(CC[0]))
            self.refresh()
        scr.refresh()
        curses.curs_set(1)
        box = Textbox(win)
        box.edit()
        m = box.gather()
        curses.curs_set(0)
        value = m.strip()
        del win
        self.wcleardraw(self.scr,pi.x-1, pi.y-1, w+2, h+4)
        self.refresh()
        self.update_all()
        return value

    def rect(self,x,y,w,h):
        wrect(self.scr,x,y,w-2,h-2,ccp(CC[0]))

    def select_colortheme(self,name):
        global CC
        if name in list(CThemes.keys()):
            CC = CThemes[name]
        else:
            CC = CThemes['default']
        self.scr.bkgd(' ', ccp(CC[0]))
