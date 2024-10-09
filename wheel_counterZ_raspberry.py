import RPi.GPIO as GPIO
import time
import sys
import os
import datetime
import csv
import json
import github
from datetime import datetime

# Set up GPIO
# Sensors 1-4 will be connected to GIPO 05, 06, 13, 19

sensor_names = {
    "D3": "Sensor 1",
    "D4": "Sensor 2",
    "D5": "Sensor 3",
    "D6": "Sensor 4",
    "D7": "Sensor 5",
    "D8": "Sensor 6",
    "D9": "Sensor 7",
    "D41": "Sensor 8"
}

# import secrets
from secrets import secrets
github_repo = secrets['github_repo']

# Replace with your GitHub username and personal access token (PAT)
github_username = secrets['github_username']
github_token = secrets['github_token']

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Initialize variables by reading the hall_effect_sensor_i.txt files
def initialize_hall_sensor_counter(filename):
    try:
        with open(f"/place1/{filename}", "r") as f:
            lines = f.readlines()
            max_count = 0
            for line in lines:
                parts = line.split(",")
                if len(parts) > 1 and "Count" in parts[1]:
                    count = int(parts[1].split(":")[1].strip())
                    if count > max_count:
                        max_count = count
            return max_count
    except FileNotFoundError:
        return 0

# Initialize counters
hall_effect_sensor_1_count = initialize_hall_sensor_counter("hall_effect_sensor_1.txt")
hall_effect_sensor_2_count = initialize_hall_sensor_counter("hall_effect_sensor_2.txt")
hall_effect_sensor_3_count = initialize_hall_sensor_counter("hall_effect_sensor_3.txt")
hall_effect_sensor_4_count = initialize_hall_sensor_counter("hall_effect_sensor_4.txt")

# Define the GPIO pins for the hall sensors
hall_sensor_pins = [5, 6, 13, 19]

# Set up GPIO pins using a for loop
for pin in hall_sensor_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def write_to_file(filename, message):
    with open(f"/place1/{filename}", "a") as f:
        f.write(message + "\n")

def update_github_file(filename, message):
    write_to_file(filename, message)
    g = github.Github(github_token)
    repo = g.get_repo(github_repo)
    contents = repo.get_contents(filename)
    repo.update_file(contents.path, f"Updated {filename}", message, contents.sha)

def sensorCallback(channel):
    timestamp = time.time()
    stamp = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    if GPIO.input(channel):
        print("Sensor HIGH " + stamp)
    else:
        print("Sensor LOW " + stamp)

def main():
    sensorCallback(5)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()

print("Setup GPIO pin as input on GPIO5")
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(5, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

if __name__ == "__main__":
    main()