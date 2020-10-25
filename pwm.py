# -*- coding: utf-8 -*-
#!/usr/bin/env python3
from enum import Flag, auto


class PWMMode(Flag):
    default = auto()
    reversed = auto()
    reranged = auto()
    RERE = reversed | reranged


class PWM():
    def __init__(self,base,port,value=0,mode=PWMMode.default,s=0,e=100,locked=False):
        self.base = base
        self.port = port
        self.value = value
        self.mode = mode
        self.rerange = [s,e]
        self.enabled = True
        self.locked = locked

    def getconf(self):
        return [self.value, self.mode.value, self.rerange[0], self.rerange[1], self.enabled]

    def set(self,value):
        #if type(value) is str:
        value = int(value)
        self.value = value
        if self.enabled == False:
            value = 0
        if self.mode & PWMMode.reranged:
            value += self.rerange[0]
            value = (value * self.rerange[1])/100

        if self.mode & PWMMode.reversed:
            value = 100 - value

        value = int(value)
        v = int((4095*value)/100)
        self.base.set_pwm(self.port,0,v)

    def setrerange(self,start,end):
        self.rerange = [start,end]

    def get(self):
        return self.value
    def enable(self):
        self.enabled = True
    def disable(self):
        self.enabled = False
    def lock(self):
        self.locked = True
    def unlock(self):
        self.locked = False

class PWM9685():
    def __init__(self,locked=False):
        self.ports = [None]*16
        self.locked = locked
        if locked == False:
            import Adafruit_PCA9685
            self.PWMFREQ = 1000
            self.basepwm = Adafruit_PCA9685.PCA9685()
            self.basepwm.set_pwm_freq(self.PWMFREQ)


    def add(self,port,value,mode=PWMMode.default,s=0,e=100):
        if not self.locked and self.ports[port] is None:
            self.ports[port] = PWM(self.basepwm,port,value,mode,s,e)
    def remove(self,port,value):
        if self.ports[port] is not None:
            if value is not None:
                self.ports[port].set(value)
            self.ports[port] = None

    def set(self,port,value):
        if not self.locked and self.ports[port] is not None:
            if value is not None:
                self.ports[port].set(value)
    def get(self,port):
        if self.ports[port] is not None:
            return self.ports[port].get()
        else:
            return -1
    def getmode(self,port):
        if self.ports[port] is not None:
            return self.ports[port].mode
    def setmode(self,port,mode):
        if self.ports[port] is not None:
            self.ports[port].mode = mode
    def addmode(self,port,mode):
        if self.ports[port] is not None:
            self.ports[port].mode |= mode
    def submode(self,port,mode):
        if self.ports[port] is not None:
            self.ports[port].mode &= ~mode
    def changemode(self,port,mode):
        if self.ports[port] is not None:
            self.ports[port].mode = not (self.ports[port].mode & ~mode)
    def get_config(self):
        r = [None]*16
        for i in range(16):
            if self.ports[i] is None:
                r[i]=[0, 0, 0,100, False]
            else:
                r[i]=self.ports[i].getconf()
        return r
    def enable(self,port):
        if self.ports[port] is not None:
            self.ports[port].enable()
    def disable(self,port):
        if self.ports[port] is not None:
            self.ports[port].disable()
    def isenabled(self,port):
        if self.ports[port] is not None:
            return self.ports[port].enabled

#rpwm = PWM9685()
