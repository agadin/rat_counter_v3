# this is a new version of coe.py that works on a raspberry pi using regular python

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

# Set up GPIO pins

# Initialize variables by reading the hall_effect_sensor_i.txt files
# Read the file and initialize the variables

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

# make a for loop to intialize the variables
hall_effect_sensor_1_count = initialize_hall_sensor_counter("hall_effect_sensor_1.txt")
hall_effect_sensor_2_count = initialize_hall_sensor_counter("hall_effect_sensor_2.txt")
hall_effect_sensor_3_count = initialize_hall_sensor_counter("hall_effect_sensor_3.txt")
hall_effect_sensor_4_count = initialize_hall_sensor_counter("hall_effect_sensor_4.txt")
# Setup Hall sensors pins
# Define the GPIO pins for the hall sensors
hall_sensor_pins = [5, 6, 13, 19]

# Set up GPIO pins using a for loop
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
hall_sensor_1_pin=GPIO.input(5)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
hall_sensor_2_pin=GPIO.input(6)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
hall_sensor_3_pin=GPIO.input(13)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
hall_sensor_4_pin=GPIO.input(19)

def write_to_file(filename, message):
    with open(f"/place1/{filename}", "a") as f:
        f.write(message + "\n")

# Function to update a file on Github with the current IP address
def update_github_file(filename, message):
    # Create a new file with the current IP address
    write_to_file(filename, message)

    # Commit the file to the GitHub repo
    g = github.Github(github_token)
    repo = g.get_repo(github_repo)
    contents = repo.get_contents(filename)
    repo.update_file(contents.path, f"Updated {filename}", message, contents.sha)

#main loop
while True:
    if not hall_sensor_1_pin.value and hall_1:
        hall_effect_sensor_1_count += 1
        sensor_name = sensor_names.get("D5", "Unknown Sensor")
        from datetime import datetime

        # Replace get_rtc_time() with datetime.now().strftime()
        message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Count: {hall_effect_sensor_1_count}, Pin: D5, Sensor Name: {sensor_name}"
        write_to_file("hall_effect_sensor_1.txt", message)
        # flash_led((255, 0, 0))  # Red for sensor 1
        print(message)  # Debug print
        hall_1 = False

    # add a delay
    time.sleep(0.05)
    if hall_sensor_1_pin.value:
        hall_1 = True

    # only runs every 60 minutes
    if datetime.now().minute % 60 == 0:
        # make the message for the commit include the time, date, sensor name, and count
        sensor_name = sensor_names.get("D5", "Unknown Sensor")
        message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Count: {hall_effect_sensor_1_count}, Pin: D5, Sensor Name: {sensor_name}"
        update_github_file("hall_effect_sensor_1.txt", message)
        # check to see if IP address has changed in ip.txt. if yes update file on github
        with open("/place1/ip.txt", "r") as f:
            ip = f.read().strip()
            # get current IP address
            current_ip = os.popen("hostname -I").read().strip()
            if ip != current_ip:
                update_github_file("ip.txt", ip)
                current_ip = ip
        # update_github_file("hall_effect_sensor_2.txt", message)
        # update_github_file("hall_effect_sensor_3.txt", message)
        # update_github_file("hall_effect_sensor_4.txt", message)
        print("Updated GitHub files")
        time.sleep(60)