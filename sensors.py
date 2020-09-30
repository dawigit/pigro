# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import adafruit_dht as dht0
import w1thermsensor
from HIH7130 import HIH7130

DHT_PIN = 23    #GPIO23 = PIN 16

class Sensor():
    def __init__(self,name): #,readvalues,getvalue,valuelist):
        self.name = name
        self.value = None
    def get(self):
            return self.value
    def getstr(self):
            return str(self.value)

#        self.readvalues = readvalues
#        self.getvalue = getvalue
#        self.valuelist = valuelist

class W1(Sensor):
    def __init__(self,w1,name=None):
        super().__init__(name if name else 'W1')
        self.w1 = w1
        self.value = w1.get_temperature()

    def read(self):
        self.value = w1.get_temperature()

class HIH(Sensor):
    def __init__(self,hih):
        super().__init__('HIH')
        self.hih = hih
        self.value = self.hih.read_hum_temp()
    def read(self):
        self.value = self.hih.read_hum_temp()

class DHT(Sensor):
    def __init__(self,dht):
        super().__init__('DHT')
        self.dht = dht
        self.value = {'h': self.dht.humidity, 'c': self.dht.temperature}
    def read(self):
        self.value = {'h': self.dht.humidity, 'c': self.dht.temperature}


class Sensors():
    def __init__(self):
        self.sensors = {}
        try:
            self.w1 = w1thermsensor.W1ThermSensor()
        except:
            self.w1 = None
        if self.w1:
            self.w1s = self.w1.get_available_sensors()
            l = len(self.w1s)
            for i in range(l):
                self.addsensor(W1(self.w1s[i],'W1'+str(i)))

#        try:
#            self.dht = dht0.DHT22(DHT_PIN)
#        except:
#            self.dht = None
#        if self.dht:
#            self.addsensor(DHT(self.dht))

        try:
            self.hih = HIH7130()
        except:
            self.hih = None
        if self.hih:
            self.addsensor(HIH(self.hih))

    def addsensor(self,sensor):
        self.sensors[sensor.name] = sensor


sen = Sensors()
