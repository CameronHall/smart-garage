# Libraries
import os
import RPi.GPIO as GPIO
import time
import pickle

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)


class DoorStatus:
    MOVEMENT_DURATION = 16.2
    OPEN_DISTANCE = 300

    DIRECTION_DOWN = 0
    DIRECTION_UP = 1

    def __init__(self):
        self.in_motion = False
        self.time_movement_end = time.time()
        self.moving_direction = None
        self.status = self.get_initial_status()

    def get_status(self):
        return self.status

    def move(self, direction):
        self.in_motion = True
        self.time_movement_end = time.time() + self.MOVEMENT_DURATION
        self.moving_direction = direction

    def is_moving(self, direction=None):
        if not self.in_motion:
            return False

        if self.time_movement_end <= time.time():
            self.reset_state_after_movement()

        if direction is None:
            return True

        return direction == self.moving_direction

    def get_initial_status(self):
        sensor = UltraSonicSensor()
        return sensor.get_average_measurement() > self.OPEN_DISTANCE

    def reset_state_after_movement(self):
        self.status = self.moving_direction
        self.moving_direction = None
        self.in_motion = False


class UltraSonicSensor:
    # set GPIO Pins
    GPIO_TRIGGER = 18
    GPIO_ECHO = 24

    CALIBRATION_COUNT = 3

    # set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    def get_average_measurement(self):
        # The sensor isn't always accurate. Let's average out the measurements
        distances = []
        for x in range(self.CALIBRATION_COUNT):
            distances.append(self.distance())
            time.sleep(0.25)

        avg = sum(distances) / self.CALIBRATION_COUNT
        return avg

    def distance(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)

        start_time = time.time()
        stop_time = time.time()

        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            start_time = time.time()

        # save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            stop_time = time.time()

        # time difference between start and arrival
        time_elapsed = stop_time - start_time
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2

        return distance


class Door:
    GPIO_RELAY = 23
    GPIO.setup(GPIO_RELAY, GPIO.OUT)

    def __init__(self):
        if os.path.isfile('status.pkl'):
            self.status = pickle.load(open('status.pkl', 'rb'))
        else:
            self.status = DoorStatus()

    def trigger_door_relay(self):
        GPIO.output(self.GPIO_RELAY, True)
        time.sleep(0.25)
        GPIO.output(self.GPIO_RELAY, False)
        time.sleep(0.25)

    def toggle_door(self, direction):
        # Door is already opening this way
        if self.status.is_moving(direction):
            return False

        # Door is moving opposite direction, let's stop that.
        print(direction, not direction, self.status.is_moving(not direction))
        if self.status.is_moving(not direction):
            self.trigger_door_relay()

        self.trigger_door_relay()
        self.status.move(direction)
        pickle.dump(self.status, open('status.pkl', 'wb'))
        return True

    def open(self):
        return self.toggle_door(DoorStatus.DIRECTION_UP)

    def close(self):
        return self.toggle_door(DoorStatus.DIRECTION_DOWN)
