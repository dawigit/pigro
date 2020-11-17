# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import base
import adafruit_dht as dht0
import w1thermsensor
from HIH7130 import HIH7130

DHT_PIN = 23    #GPIO23 = PIN 16

class Sensor(base.ControlObject):
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.value = None
        self.valueisdict = False
    def get(self):
            return self.value
    def __str__(self):
            return str(self.value)
    def read(self):
        None
    def __repr__(self):
        return str(self.value)
    def __getitem__(self,index):
        #if index is not None:
        return self.value[index]
#        else:
#            return str(self.value)

class W1(Sensor):
    def __init__(self,w1,name=None):
        super().__init__(name if name else 'W1')
        self.w1 = w1
        self.value = self.w1.get_temperature()

    def read(self):
        self.value = self.w1.get_temperature()

class HIH(Sensor):
    def __init__(self,hih):
        super().__init__('HIH')
        self.hih = hih
        self.value = self.hih.read_hum_temp()
        self.valueisdict = True
    def read(self):
        self.value = self.hih.read_hum_temp()

class DHT(Sensor):
    def __init__(self,dht):
        super().__init__('DHT')
        self.dht = dht
        self.value = {'h': self.dht.humidity, 'c': self.dht.temperature}
        self.valueisdict = True
    def read(self):
        self.value = {'h': self.dht.humidity, 'c': self.dht.temperature}


class Sensors():
    def __init__(self):
        self.sensors = {}
        self.vsensors = {}
        try:
            self.w1 = w1thermsensor.W1ThermSensor()
        except:
            self.w1 = None
        if self.w1:
            self.w1s = self.w1.get_available_sensors()
            l = len(self.w1s)
            for i in range(l):
                self.addsensor(W1(self.w1s[i],'W1'+str(i)))

        try:
            self.dht = dht0.DHT22(DHT_PIN)
            if self.dht:
                self.addsensor(DHT(self.dht))
        except:
            self.dht = None

        try:
            self.hih = HIH7130()
            if self.hih:
                self.addsensor(HIH(self.hih))
        except:
            self.hih = None

    def addsensor(self,sensor):
        self.sensors[sensor.name] = sensor

    def getsensorkeys(self,name):
        if type(self.sensors[name].value) is dict:
            return list(self.sensors[name].value.keys())
    def isvaluedict(self,name):
        return True if type(self.sensors[name].value) is dict else False
    def getall(self):
        d = {}
        for k in list(self.sensors.keys()):
            d[self.sensors[k].name] = self.sensors[k].get()
        return d

sen = Sensors()
