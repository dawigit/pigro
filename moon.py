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
        return rise[int(p/33)]
    else:
        return fall[3-int(p/33)]

def get_phase():
    global location
    o = ephem.Observer()
    o.long = location.longitude
    o.lat = location.latitude
    o.name = location.address
    #o = ephem.city("city")
    m = ephem.Moon(o)
    return m.phase
