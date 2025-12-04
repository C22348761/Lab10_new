import umqtt.robust as umqtt
from network import WLAN
import time
from machine import ADC
import json
from ws2812 import WS2812
from machine import Pin
import sensor_upb2 as sensor
BROKER_IP = "172.20.10.5"
TOPIC = b'temp/pico'
OUTPUT_PIN = 'LED'
PUB_INDENT = 'pico'
latest_readings = {} 
wifi = WLAN(WLAN.IF_STA)
wifi.active(True)
wifi.connect("Samsung s4", "12345678")
latest_readings = {}
while not wifi.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Connected! IP:", wifi.ifconfig()[0])

# --- MQTT for the PI ---
HOSTNAME = '172.20.10.5'  
PORT = 8080


mqtt = umqtt.MQTTClient(
    client_id=b'pico_2',
    server=BROKER_IP, 
    port=PORT,
    keepalive=7000
)
mqtt.connect()
latest_readings = {}

temp_sensor = ADC(4)

def read_temp():
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 65535)
    temperature = 27 - (voltage - 0.706)/0.001721
    return temperature


led = Pin(OUTPUT_PIN, machine.Pin.OUT)

def update_outputs(avg):
    if avg < 0: avg = 0
    if avg > 20: avg = 20
    s = int(avg * 12.75)
    led.set_pixel(0, s, 0, 255 - s)
    led.show()

'''
def callback(topic, msg):
    data = json.loads(msg)
    pid = data["id"]
    temp = float(data["temp"])
    ts = float(data["time"])

    latest_readings[pid] = {"temp": temp, "time": ts}

    now = time.time()
    valid = [
        v["temp"]
        for v in latest_readings.values()
        if now - v["time"] <= 600
    ]

    if valid:
        avg = sum(valid) / len(valid)
        print("Average temp:", avg)
        update_outputs(avg)
'''
def callback(topic, msg):
    data = sensor.SensorreadingMessage()
    data.parse(msg)

    print("Publisher:", data.publisher_id)
    print("Temp:", data.temperature)
    print("Time:", data.timestamp._value)
    if data.temperature._value > 25:
        led.value(1)
    else:
        led.value(0)
        
    latest_readings[data.publisher_id] = {"temp": data.temperature._value, "time": data.timestamp._value}
   
    now = int(time.time())
    for key in list(latest_readings):  
        if now - latest_readings[key]["time"] > 600:  
            del latest_readings[key]
        
   
if OUTPUT_PIN is None:
   # mqtt.set_callback(callback)
    while True:
        print("Pub mode")
        temp = read_temp()
        data = sensor.SensorreadingMessage()
        data.temperature = temp
        data.publisher_id = 'pico'
        data.timestamp.epoch= time.time()
        
        payload = data.serialize()
        mqtt.publish(TOPIC, payload)
        print("Published:", temp, payload)
        time.sleep(2)

else:
    mqtt.set_callback(callback)
    mqtt.subscribe(TOPIC)
    while True:
        print("Sub mode")
        mqtt.wait_msg()


