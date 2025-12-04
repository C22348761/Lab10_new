# Lab10 - Raspberry Pi Pico MQTT Temperature Sensor

A MicroPython project for Raspberry Pi Pico that publishes and subscribes to temperature sensor readings via MQTT using Protocol Buffers for efficient message serialization.

## Overview

This project implements a distributed temperature monitoring system where multiple Raspberry Pi Pico devices can:
- **Publish** temperature readings from their onboard sensors
- **Subscribe** to temperature readings from other devices
- Use Protocol Buffers for compact, efficient message serialization over MQTT

## Features

- 🌡️ Onboard temperature sensor reading (ADC channel 4)
- 📡 MQTT pub/sub communication
- 🔌 Protocol Buffer message serialization
- 📶 WiFi connectivity
- 💡 LED output control (subscriber mode)
- ⏱️ Automatic cleanup of stale readings (10-minute window)

## Hardware Requirements

- Raspberry Pi Pico (or Pico W)
- MQTT broker (configured at `172.20.10.5:8080`)
- WiFi network access

## Files

- **`lab8_pub.py`** - Publisher implementation (publishes temperature readings)
- **`sub22.py`** - Subscriber implementation (receives readings and controls LED)
- **`sensor.proto`** - Protocol Buffer definition for sensor messages
- **`sensor_upb2.py`** - MicroPython Protocol Buffer implementation using uprotobuf
- **`uprotobuf.py`** - Core Protocol Buffer library for MicroPython (required dependency)

## Configuration

### WiFi Settings
Update the WiFi credentials in both files:
```python
wifi.connect("Samsung s4", "12345678")
```

### MQTT Broker
Configure the broker IP and port:
```python
BROKER_IP = "172.20.10.5"
PORT = 8080
```

### MQTT Topic
Default topic: `temp/pico`

## Usage

### Publisher Mode (`lab8_pub.py`)
- Sets `OUTPUT_PIN = None` to enable publisher mode
- Reads temperature from onboard sensor every 2 seconds
- Publishes readings as Protocol Buffer messages
- Client ID: `pico_1`

### Subscriber Mode (`sub22.py`)
- Sets `OUTPUT_PIN = 'LED'` to enable subscriber mode
- Subscribes to temperature topic
- Controls LED based on temperature threshold (>25°C)
- Maintains a rolling window of readings (10 minutes)
- Client ID: `pico_2`

## Protocol Buffer Schema

The sensor reading message structure:
```protobuf
message sensorReading {
    required float temperature = 1;
    required string publisher_id = 2;
    required uint64 timestamp = 3;
}
```

## Dependencies

- `umqtt.robust` - MQTT client library
- `uprotobuf.py` - Protocol Buffer implementation for MicroPython (included in project)
- `ws2812` / `ws2182` - LED control (publisher mode)
- `machine` - Hardware interface (ADC, Pin)

## Installation

1. Flash MicroPython to your Raspberry Pi Pico
2. Install required libraries via `mip` or copy to device
3. Upload all files to the Pico
4. Configure WiFi and MQTT broker settings
5. Run the appropriate script for your use case

## Notes

- Temperature readings are automatically cleaned up after 10 minutes
- Publisher uses WS2812 LED for visual feedback
- Subscriber uses a simple GPIO LED that turns on when temperature > 25°C
- The system supports multiple publishers with unique publisher IDs

