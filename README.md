# PiGro #

## PiGro allows you to: ##

- read thermal & humidity sensors
- control pwm driven fans and led drives
- switch between 12/12 and 18/6 cycle
- maintenance mode for better eye protection from strong light sources
- automatically turn the light on and off
- automatically change power of led and out fan upon sensor values
- keep track of the moonphase

## Hardware setup: ##

- Raspberry Pi ZeroW (any RaspberryPi will work)
- PWM servo driver hat PCA9685
- DS18B20 thermo sensor (Maxim Integrated)
- HIH7121 humidity/thermo sensor (Honeywell, for high humidity scenarios)
- optional: DHT-xx/AM230x (only for external measurements - NOT for high humidity scenarios)
- ELG-240-42AB led driver (Meanwell)
- Zeus compact led board 2x (Led-Tech)
- Bitfenix 200mm fan for cooling the led boards
- optional: converter for pwm to 0-10v for non-pwm fans or meanwell hlg600
- Noctua PWM fan for outgoing air


## Installation: ##

The led driver is controlled via **PWM0**.
The outgoing air fan is controlled via **PWM15**.


OneWire/DS18B20: **GPIO4**
add the following to your raspberry pi's `/boot/config.txt`:
`dtoverlay=w1-gpio,gpiopin=4`

HIH7121
connect to i2c1


## Enabling the interfaces ##
`sudo raspi-config`
-> `Interfacing-Options` -> enable `I2C`, enable `1-Wire`


## Getting your Raspberry Pi ready ##

`sudo apt install python3 python3-{venv,dev,libgpiod,smbus}`

`git clone https://github.com/dawigit/pigro.git`

`cd pigro`

`python3 -m pip install -r requirements.txt`

`python3 pigro.py`

![Screenshot](img_pigro.png)
