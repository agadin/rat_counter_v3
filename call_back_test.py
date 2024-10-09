try:
    while True:
        state = GPIO.input(HALL_SENSOR_PIN)
        if state:
            print("Magnetic field detected!")
        else:
            print("Magnetic field lost!")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()  # Clean up GPIO settings

