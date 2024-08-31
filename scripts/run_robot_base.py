#!/usr/bin/env python3
import serial
import time
import glob
import argparse
import matplotlib.pyplot as plt
import datetime

# USB port
ser = None

def main():
    open_robot()

    action = [20.0, 0.0, 0.0,  20.0, 0.0, 0.0]
    send_action(action)

def open_robot():
    global ser
    port_pattern = '/dev/tty.usbmodem*'
    port = find_serial_port(port_pattern)
    baudrate = 115200
    try:
        # Open the serial port
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baudrate.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except IOError as e:
        print(f"I/O error: {e}")
    except KeyboardInterrupt:
        print("Program interrupted.")

def send_action(action):
    # Write packet
    global ser
    byte_array = bytearray([0x61, 0x1, int(action[0]), int(action[1]), int(action[2]), int(action[3]), int(action[4]), int(action[5])])
    ser.write(byte_array)
    print(f"Wrote: {action[0]}...")

def find_serial_port(pattern):
    ports = glob.glob(pattern)
    if ports:
        return ports[0]
    else:
        raise IOError("No serial ports found matching the pattern")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot send receive script")
    args = parser.parse_args()
    main()