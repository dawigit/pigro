# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import ephem
from datetime import datetime
from geopy import geocoders
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent='none')
location = None
loc = "Munich, Germany"

rise = ["🌑","🌒","🌓","🌔"]
fall = ["🌕","🌖","🌗","🌘"]

def set_location(loc):
    global location
    location = geolocator.geocode(loc)

def get_moon():
    global location
    o = ephem.Observer()
    o.long = location.longitude
    o.lat = location.latitude
    o.name = location.address

    #o = ephem.city("city")
    m = ephem.Moon(o)
    p = m.phase
    dnm = ephem.next_new_moon(datetime.now()).datetime()
    dfm = ephem.next_full_moon(datetime.now()).datetime()
    if dnm > dfm:
        if p>=0 and p<5:
            return rise[0]
        if p>=5 and p<35:
            return rise[1]
        if p>=35 and p<70:
            return rise[2]
        if p>70 and p<90:
            return rise[3]
        if p>=90:
            return fall[0]
    else:
        if p<=100 and p>80:
            return fall[0]
        if p<=80 and p>60:
            return fall[1]
        if p<=60 and p>40:
            return fall[2]
        if p<=40 and p>10:
            return fall[3]
        if p<10:
            return rise[0]

def get_phase():
    global location
    o = ephem.Observer()
    o.long = location.longitude
    o.lat = location.latitude
    o.name = location.address
    #o = ephem.city("city")
    m = ephem.Moon(o)
    return m.phase
