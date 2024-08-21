# Flow Sensor Driver



## Hardware

### Materials
- Arduino Mega 2560
- Alicat MFC
- Flow sensor
- Air supply
- 10V power supply


### Setup

- Connect flow sensor output to Arduino pin A0
- Connect flow sensor to 10V power supply - make sure flow sensor, Arduino, and power supply are grounded together
- Connect Arduino to computer (upload sketch, open GUI)

#

<br>

## read_flow_sensor.ino
Arduino code to use with python driver: Reads & prints flow sensor value from pin A0
- 9600 baudrate
- 50ms between each value

<br>

## flow_sensor_driver.py

Calibration section allows for running flow sensor calibrations (& saving file), same as in olfactometer widget.
Stats of calibration are displayed in GUI and in logger