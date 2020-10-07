# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import Adafruit_PCA9685
from enum import Flag, auto
from base import BaseUtil

ModePWMDefault = 0
ModePWMReversed = 1

PWMFREQ = 1000
basepwm = Adafruit_PCA9685.PCA9685()
basepwm.set_pwm_freq(PWMFREQ)

class PWMMode(Flag):
    default = auto()
    reversed = auto()
    reranged = auto()
    RERE = reversed | reranged


class PWM(BaseUtil):
    def __init__(self,port,value=0,mode=PWMMode.default,s=0,e=100):
        self.port = port
        self.value = value
        self.mode = mode
        self.rerange = [s,e]
        self.enabled = True

    def set(self,value):
        if type(value) == str:
            value = int(value)
        if self.enabled == False:
            value = 0
        if self.mode & PWMMode.reranged:
            value += self.rerange[0]
            value = (value * self.rerange[1])/100

        if self.mode & PWMMode.reversed:
            value = 100 - value

        value = int(value)
        v = int((4095*value)/100)
        self.value = v
        basepwm.set_pwm(self.port,0,v)

    def setrerange(self,start,end):
        self.rerange = [start,end]

    def get(self):
        return self.value

class PWM9685():
    def __init__(self):
        self.ports = [None]*16

    def add(self,port,value,mode=PWMMode.default,s=0,e=100):
        if self.ports[port] is None:
            self.ports[port] = PWM(port,value,mode,s,e)

    def remove(self,port,value):
        if self.ports[port] is not None:
            if value is not None:
                self.ports[port].set(value)
            self.ports[port] = None

    def set(self,port,value):
        if self.ports[port] is not None:
            if value is not None:
                self.ports[port].set(value)
    def get(self,port):
        if self.ports[port] is not None:
            return self.ports[port].get()
        else:
            return -1
rpwm = PWM9685()