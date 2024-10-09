import smbus2
import time

def scan_i2c():
    bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1
    print("Scanning I2C bus for devices...")

    for address in range(0x03, 0x78):
        try:
            bus.write_byte(address, 0)
            print(f"Found device at address: 0x{address:02X}")
        except OSError:
            pass  # No device at this address

    bus.close()
    print("Scan complete.")

if __name__ == "__main__":
    scan_i2c()