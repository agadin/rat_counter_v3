from rpi_lcd import LCD
from time import sleep

# Initialize the LCD
lcd = LCD()

# Function to update the LCD display
def update_lcd_display():
    try:
        # Read the current counts
        count1 = globals().get('hall_effect_sensor_1_count', 0)
        count2 = globals().get('hall_effect_sensor_2_count', 0)
        count3 = globals().get('hall_effect_sensor_3_count', 0)
        count4 = globals().get('hall_effect_sensor_4_count', 0)

        # Update the LCD display
        lcd.text(f"1:{count1} 2:{count2}", 1)
        lcd.text(f"3:{count3} 4:{count4}", 2)
    except Exception as e:
        log_error(f"Error updating LCD display: {e}")

# Example usage
update_lcd_display()
sleep(5)
lcd.clear()