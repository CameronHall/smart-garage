# Libraries
from flask import Flask
from door import Door, UltraSonicSensor
import RPi.GPIO as GPIO

try:
    app = Flask(__name__)
except InterruptedError:
    GPIO.cleanup()

door = Door()


@app.route('/status')
def status():
    distance = UltraSonicSensor().get_average_measurement()
    result = 'Open' if door.status.get_status() else 'Closed'
    return result + ' ' + str(distance)


@app.route('/open')
def open_door():
    return 'Done' if door.open() else 'No'


@app.route('/close')
def close_door():
    return 'Done' if door.close() else 'No'
