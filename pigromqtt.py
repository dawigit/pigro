# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as ppublish
import json
import logging

client = mqtt.Client()
client.username_pw_set(username="pi", password="pigro")
client.connect("pi4", 1883, 60)
client.loop_start()

def disconnect():
    client.disconnect()

def pub(topic,data):
    client.publish(topic,data)
