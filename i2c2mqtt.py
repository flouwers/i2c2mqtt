#!/usr/bin/env python3
# -*- coding: latin-1 -*-
#
#  i2c2mqtt.py
#
#  Copyright 2016 Sébastien Lucas <sebastien@slucas.fr>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#

import bh1750
#import bme280
#import si7021
import ccs811
import time, json, argparse
import paho.mqtt.publish as publish # pip install paho-mqtt
import paho.mqtt.client as mqtt

verbose = False
ccs811setup = False

def debug(msg):
  if verbose:
    print (msg + "\n")

def getbh1750():
  # Drop the first (usually bad)
  lux = bh1750.readLight()
  lux = bh1750.readLight()
  return lux

def getsi7021():
  T = si7021.readTemperature()
  RH = si7021.readHumidity()
  return T,RH

def getbme280():
  T, P, RH = bme280.readBME280All()
  return T, P, RH

def getccs811():
  global ccs811setup
  if not ccs811setup:
    ccs811.setup()
    ccs811setup = True
  if ccs811.data_available():
    co2, tvoc = ccs811.read_logorithm_results()
  elif self.check_for_error():
    self.print_error()
  return co2, tvoc

def setupMqtt(broker_address):
  print("creating new instance")
  client = mqtt.Client("P1") #create new instance
  print("connecting to broker")
  client.connect(broker_address) #connect to broker

def publishMqtt(topic, message):
  print("Publishing message", message," to topic ", topic)
  client.publish(topic,message)


parser = argparse.ArgumentParser(description='Read current temperature,illuminance and humidity from i2c sensors and send them to a MQTT broker.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-d', '--device', dest='devices', action="append",
                   help='Specify the devices to probe in the I2C bus. Can be called many times.')
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/i2c",
                   help='The MQTT topic on which to publish the message (if it was a success).')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/sensor/i2c", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')

args = parser.parse_args()
verbose = args.verbose;


setupMqtt(args.host)

while (True):
  if not isinstance(args.devices, list):
    print ("No devices specified")
    exit()

  if 'bh1750' in args.devices:
    lux = getbh1750()
    publishMqtt(args.topic , "/bh1750", lux)

  if 'si7021' in args.devices:
    t, rh = getsi7021()
    publishMqtt(args.topic + "/si7021", t)
    publishMqtt(args.topic + "/si7021", rh)

  if 'bme280' in args.devices:
    t, p, rh = getbme280()
    publishMqtt(args.topic + "/bme280", t)
    publishMqtt(args.topic + "/bme280", p)
    publishMqtt(args.topic + "/bme280", rh)

  if 'ccs811' in args.devices:
    co2, tvoc = getccs811()
    publishMqtt(args.topic + "/ccs811", co2)
    publishMqtt(args.topic + "/ccs811", tvoc)



#if status:
#  debug("Success with message (for current readings) <{0}>".format(jsonString))
##  if not args.dryRun:
#    publish.single(args.topic, jsonString, hostname=args.host)
#else:
#  debug("Failure with message <{0}>".format(jsonString))
#  if not args.dryRun:
#    publish.single(args.topicError, jsonString, hostname=args.host)

