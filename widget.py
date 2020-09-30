# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import curses
from curses.textpad import rectangle
S_CURSOR = "👉"
S_CLOCK = "⏰"
W_FRAME = 0x01
W_NOCIRCLE = 0x02
W_LIVE = 0x04

scr = curses.initscr()
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

h24 = []
h24us = []
m60 = []
percent = []

for i in range(24):
    h24.append(str(i).zfill(2))
for i in range(13):
    h24us.append(str(i).zfill(2)+" AM")
for i in range(13):
    h24us.append(str(i).zfill(2)+" PM")
for i in range(60):
    m60.append(str(i).zfill(2))
for i in range(11):
    percent.append('{:>3}'.format(str(i*10)))

def rect(scr,x,y,w,h):
    rectangle(scr,y,x,y+h,x+w)

class BaseWidget():
    def __init__(self, scr):
        self.scr = scr

class Widget(BaseWidget):
    def __init__(self,scr):
        super().__init__(scr)
        self.onunfocus = None
        self.onchange = None
        self.focused = False
        self.nofocus = False

    def focus(self):
        self.focused = True
        return 0

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

    def draw(self):
        None

class WidgetNoFocus(BaseWidget):
    def __init__(self,scr):
        super().__init__(scr)
        self.scr = scr
        self.nofocus = True

    def focus(self):
        return 1

    def unfocus(self):
        None

    def draw(self):
        None

class WidgetLabel(WidgetNoFocus):
    def __init__(self, scr, label, x,y):
        super().__init__(scr)
        self.scr = scr
        self.label = label
        self.x = x
        self.y = y
        self.nofocus = True

    def draw(self):
        self.scr.addstr(self.y,self.x,self.label)

    def set_label(self,label):
        self.label = label


class WidgetLabelValue(WidgetLabel):
    def __init__(self, scr, label, x,y, value, getvalue=None, arg=None):
        super().__init__(scr, label, x,y)
        self.value = value
        self.get_value = getvalue
        self.arg = arg

    def draw(self,spacer=" "):
        if callable(self.get_value):
            if self.arg===None:
                self.value = self.get_value()
            else:
                self.value = self.get_value(self.arg)
        self.scr.addstr(self.y,self.x,str.format("{0:}{1:}{2:}",self.label,spacer,self.value))

    def set_value(self,value):
        self.value = value

class WidgetRoller(Widget):
    def __init__(self, scr, data, x,y,attributes=W_FRAME,selected=0,cursorposition=0,w=0,h=1):
        super().__init__(scr)
        if selected >= len(data):
            raise ValueError('selected value does not exist in data')
        self.scr = scr
        self.x = x
        self.y = y
        self.attributes = attributes
        if w == 0:
            for d in data:
                if len(d) > w:
                    w = len(d)
        self.w = w
        self.h = h
        self.data = data
        self.selected = selected
        self.cursorposition = cursorposition
        self.ccolor = curses.color_pair(0)
        self.draw()

    def focus(self):
        super().focus()

    def unfocus(self):
        super().unfocus()
        self.draw()

    def is_focus(self):
        return super().is_focus()

    def draw(self):
        plusone = 1
        if self.attributes & W_FRAME:
            rect(scr,self.x,self.y,self.w+1,self.h+1)
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
            self.scr.addstr(self.y + i + plusone, self.x + plusone, self.data[self.cursorposition],self.ccolor)

    def select(self):
        self.selected = self.cursorposition
        self.draw()
        if callable(self.onchange):
            self.onchange(self.arg,self.data[self.selected],self.selected)



    def movecursor(self,direction):
        if self.attributes & W_NOCIRCLE:
            if self.cursorposition+direction < 0 or self.cursorposition+direction > len(self.data)-1:
                return
        self.cursorposition += direction
        if self.cursorposition < 0:
            self.cursorposition = len(self.data)-1
        if self.cursorposition > len(self.data)-1:
            self.cursorposition = 0
        if self.attributes & W_LIVE:
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


class WidgetSelect(Widget):
    def __init__(self, scr, data, x,y,attributes=0,selected=0,cursorposition=0,w=0,h=0, margin=3):
        super().__init__(scr)
        #self.id = id
        if selected >= len(data):
            raise ValueError('selected value does not exist in data')
        self.scr = scr
        self.x = x
        self.y = y
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
        self.cursorposition = cursorposition
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
        rect(scr,self.x,self.y,self.w+self.margin+2,self.h+1)
        row = 0
        for i in self.data:
            if row > self.h - 1:
                self.scr.addstr(self.y + 1 + row, self.x + 1 + self.margin, self.spacer(self.w+self.margin),self.ccolor)
                continue
            if row == self.selected:
                self.ccolor = curses.color_pair(6)
            self.scr.addstr(self.y + 1 + row, self.x + 1 + self.margin, self.data[row],self.ccolor)
            self.ccolor = curses.color_pair(0)
            row += 1
        if self.is_focus() == True:
            self.drawcursor()

    def drawcursor(self):
        self.scr.addstr(self.y + 1 + self.cursorposition,self.x + 1,S_CURSOR,self.ccolor)

    def movecursor(self,direction):
        self.scr.addstr(self.y + 1 + self.cursorposition, self.x + 1, self.spacer(self.margin),self.ccolor)
        if direction == 1 and self.cursorposition+1 < len(self.data):
            self.cursorposition += 1
        if direction == -1 and self.cursorposition > 0:
            self.cursorposition -= 1
        if self.attributes & W_LIVE:
            self.select()
        self.drawcursor()

    def removecursor(self):
        self.scr.addstr(self.y + 1 + self.cursorposition, self.x + 1, self.spacer(self.margin),self.ccolor)

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
            self.scr.addstr(self.y + y, self.x, self.spacer(self.w + 1),self.ccolor)

    def get_selected(self):
        return self.selected

class SuWidget():
    _wcounter = 0
    _wlist = []
    _wlabel = []
    _focus = 0
    def __init__(self,scr):
        self.scr = scr

    def rect(self,x,y,w,h):
        rect(self.scr,x,y,w,h)

    def add_widgetselect(self, data, x,y,attributes=0, selected=0, cursorposition=0, w=0,h=0, margin=3):
        SuWidget._focus = SuWidget._wcounter
        SuWidget._wlist.append(WidgetSelect(self.scr,data,x,y,attributes,selected,cursorposition,w,h,margin))
        SuWidget._wcounter += 1
        return SuWidget._wcounter - 1

    def add_widgetroller(self,data, x,y, attributes=W_FRAME, selected=0, cursorposition=0, w=0,h=1):
        SuWidget._focus = SuWidget._wcounter
        SuWidget._wlist.append(WidgetRoller(self.scr,data,x,y,attributes,selected,cursorposition,w,h))
        SuWidget._wcounter += 1
        return SuWidget._wcounter - 1

    def add_widgetlabel(self, label, x,y):
        SuWidget._wlabel.append(WidgetLabel(self.scr,label,x,y))
        return len(SuWidget._wlabel)-1

    def add_widgetlabelvalue(self, label, x,y, value, getvalue=None, arg=None):
        SuWidget._wlabel.append(WidgetLabelValue(self.scr,label,x,y,value,getvalue,arg))
        return len(SuWidget._wlabel)-1

    def update_label(self,id,label):
        if not type(value) == str:
            label = str(label)
        SuWidget._wlabel[id].label = label

    def update_labelvalue(self,id,label,value):
        SuWidget._wlabel[id].label = label
        if not type(value) == str:
            value = str(value)
        SuWidget._wlabel[id].value = value

    def update_labelvaluevalue(self,id,value):
        if not type(value) == str:
            value = str(value)
        SuWidget._wlabel[id].value = value

    def add_clock(self,x,y,hours,minutes):
        o = 3
        self.add_widgetlabel(S_CLOCK,x,y)
        id = self.add_widgetroller(h24,x+o,y,0,hours,hours)
        self.add_widgetlabel(":",x+o+2,y)
        self.add_widgetroller(m60,x+o+3,y,0,minutes,minutes)
        return id

    def next(self):
        SuWidget._wlist[SuWidget._focus].unfocus()
        SuWidget._focus += 1
        if SuWidget._focus == SuWidget._wcounter:
            SuWidget._focus = 0
        donext = SuWidget._wlist[SuWidget._focus].focus()
        if donext:
            self.next()
        SuWidget._wlist[SuWidget._focus].draw()
        self.drawlabels()

    def prev(self):
        SuWidget._wlist[SuWidget._focus].unfocus()
        SuWidget._focus -= 1
        if SuWidget._focus < 0:
            SuWidget._focus = SuWidget._wcounter -1
        doprev = SuWidget._wlist[SuWidget._focus].focus()
        if doprev:
            self.prev()
        SuWidget._wlist[SuWidget._focus].draw()
        self.drawlabels()

    def drawlabels(self):
        for wlabel in (SuWidget._wlabel):
            #self.scr.addstr(1,0,wlabel.get_value())
            if wlabel.label:
                wlabel.draw()

    def focus(self,id):
        if id < SuWidget._wcounter:
            SuWidget._focus = id
        donext = SuWidget._wlist[SuWidget._focus].focus()
        if donext:
            self.next()
        SuWidget._wlist[SuWidget._focus].draw()
        self.drawlabels()

    def update(self,id):
        SuWidget._wlist[id].draw()

    def onkeyboard(self,key):
        if key == curses.KEY_RIGHT:
            self.next()
        if key == curses.KEY_LEFT:
            self.prev()
        SuWidget._wlist[SuWidget._focus].onkeyboard(key)

    def get_clock(self,id):
        h = SuWidget._wlist[id].data[SuWidget._wlist[id].selected]
        m = SuWidget._wlist[id+1].data[SuWidget._wlist[id+1].selected]
        s = str.format("{0:}:{1:}",h,m)
        return s

    def set_clock(self,id,h,m):
        SuWidget._wlist[id].selected = h
        SuWidget._wlist[id].cursorposition = h
        SuWidget._wlist[id+1].selected = m
        SuWidget._wlist[id+1].cursorposition = m
        SuWidget._wlist[id+1].draw()

    def set_onchange(self,id,onchange,arg=None):
        SuWidget._wlist[id].set_onchange(onchange,arg)

    def quit(self):
        curses.nocbreak()
        self.scr.keypad(False)
        curses.resetty()
        curses.endwin()
        curses.curs_set(1)
        curses.echo(True)

    def update_all(self):
        for w in SuWidget._wlist:
            w.draw()
        self.drawlabels()
