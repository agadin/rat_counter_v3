
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

# automatic starting
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