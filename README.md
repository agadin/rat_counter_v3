
# Overview
This project is designed to count and log events from multiple hall effect sensors that count the number of times a magnet has passed by. The program can be installed on two different sets of hardware: arduino or Raspberry Pi. Both versions include an real time clock (RTC), 8 hall sensor inputs, and a character LCD display. 

* [Introduction](#introduction)
* [Installation](#installation)
* [Usage](#usage)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)

# Introduction
This project is designed to count and log events from multiple hall effect sensors. It uses a Raspberry Pi to read sensor data, process it, and store the results. The project also includes functionality to display sensor counts on an LCD and periodically push data to a GitHub repository.


# Installation


## Arduino

### Hardware
* Bee Data Logger
* 8 Hall Effect Sensors
* 16x2 Character LCD
*  5V 2004 1602 LCD Display IIC I2C Adapter IIC Serial Interface Adapter

### Wiring

### Software

**Prepare the Arduino IDE for the Bee Data Logger by following the instructions below:**
1. Download the Arduino IDE from the link above
2. Open the Arduino IDE
3. Go to File -> Preferences
4. In the Additional Boards Manager URLs field, add the following URL: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
5. Go to the library manager by going to Sketch -> Include Library -> Manage Libraries
6. Search for LiquidCrystal I2C and install the library
7. Search for ESP32 and install the library
8. Search for Bee Data Logger and install the library 

**Flashing the Bee Data Logger:**
1. Install the micro SD card into the Bee Data Logger (has to be formatted as FAT32 or FAT16)
2. Connect the Bee Data Logger to the computer
3. Put the Bee Data Logger into bootloader mode by holding down the boot button and quickly pressing the reset button. Then release the boot button. 
4. Go to Tools -> Board -> Boards Manager 
5. In Board select Bee Data Logger
6. Go to Tools -> Port and select the port that the Bee Data Logger is connected to
7. Open the rat_counter_v3.ino file in the Arduino IDE
8. Click the upload button to upload the code to the Bee Data Logger



## Raspberry Pi

### automatic starting

```
source myenv/bin/activate
sudo nano /etc/systemd/system/myscript.service

sudo systemctl daemon-reload
sudo systemctl enable myscript.service

sudo systemctl start myscript.service

sudo systemctl status myscript.service

sudo journalctl -u myscript.service -f

pip3 install adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

pip3 install adafruit-circuitpython-charlcd
sudo apt-get install python3-pip python3-dev i2c-tools
```

```
sudo cp /home/lakelab/Documents/rat_counter_v3/myscript.service /etc/systemd/system/
sudo cp /home/lakelab/Documents/rat_counter_v3/app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable myscript.service
sudo systemctl enable app.service
sudo systemctl start myscript.service
sudo systemctl start app.service
sudo systemctl status myscript.service
sudo systemctl status app.service

sudo systemctl start pigpiod
sudo systemctl enable pigpiod
sudo systemctl status pigpiod
```
```
{
    "time_between_pushes_minutes": 60,
    "sensor_names": {
        "D3": "Sensor 1",
        "D4": "Sensor 2",
        "D5": "Sensor 3",
        "D6": "Sensor 4",
        "D7": "Sensor 5",
        "D8": "Sensor 6",
        "D9": "Sensor 7",
        "D41": "Sensor 8"
    },
    "character_lcd": true,
    "uln2003_stepper": false
}
```
# Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.
* @agadin on github

# License
Distributed under the MIT License. See `LICENSE` for more information.

# Contact
* @agadin on github

# Acknowledgements
* [Raspberry Pi](https://www.raspberrypi.org/)
* [Bee Data Logger](https://github.com/strid3r21/Bee-Data-Logger/tree/main)