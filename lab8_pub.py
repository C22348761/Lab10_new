import umqtt.robust as umqtt
from network import WLAN
import time
from machine import ADC
import json
from ws2812 import WS2812
import sensor_upb2 as sensor
# MQTT Configuration
BROKER_IP = "172.20.10.5"
TOPIC = b'temp/pico'
OUTPUT_PIN = None  # None = publisher mode, set to pin name for subscriber mode
PUB_INDENT = 'pico'

wifi = WLAN(WLAN.IF_STA)
wifi.active(True)
wifi.connect("Samsung s4", "12345678")

while not wifi.isconnected():
    print("Connecting to Wi-Fi...")
    time.sleep(1)

print("Connected! IP:", wifi.ifconfig()[0])

# --- MQTT for the PI ---
HOSTNAME = '172.20.10.5'  
PORT = 8080


mqtt = umqtt.MQTTClient(
    client_id=b'pico_1',
    server=BROKER_IP, 
    port=PORT,
    keepalive=7000
)
mqtt.connect()
latest_readings = {}

# Onboard temperature sensor on ADC channel 4
temp_sensor = ADC(4)

def read_temp():
    """Read temperature from Pico's onboard sensor.
    Formula converts ADC reading to voltage, then to Celsius.
    """
    value = temp_sensor.read_u16()
    voltage = value * (3.3 / 65535)  # Convert 16-bit ADC to voltage (0-3.3V)
    temperature = 27 - (voltage - 0.706)/0.001721  # Pico-specific calibration
    return temperature

# WS2812 LED on pin 1 (not used in publisher mode, but initialized)
led = WS2812(1, 0)

def update_outputs(avg):
    """Update LED color based on average temperature.
    Maps 0-20°C to blue (0,0,255) -> red (255,0,0) gradient.
    """
    if avg < 0: avg = 0
    if avg > 20: avg = 20
    s = int(avg * 12.75)  # Scale 0-20°C to 0-255 for color mapping
    led.set_pixel(0, s, 0, 255 - s)  # Red increases, blue decreases with temp
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

  

if OUTPUT_PIN is None:
    # Publisher mode: read sensor and publish readings
    while True:
        print("Pub mode")
        temp = read_temp()
        data = sensor.SensorreadingMessage()
        data.temperature = temp
        data.publisher_id = 'pico'
        data.timestamp = int(time.time())  # Unix epoch timestamp
        
        payload = data.serialize()  # Serialize to Protocol Buffer format
        mqtt.publish(TOPIC, payload)
        print("Published:", temp, payload)
        
        time.sleep(2)  # Publish every 2 seconds

else:
    mqtt.set_callback(callback2)
    mqtt.subscribe(TOPIC)
    while True:
        
        print("Sub mode")
        mqtt.wait_msg()

