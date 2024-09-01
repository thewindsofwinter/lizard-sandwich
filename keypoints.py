#!/usr/bin/env python3
import serial
import time
import glob
import argparse
import matplotlib.pyplot as plt
import datetime
import threading
import numpy as np

# USB port
ser = None
NUM_JOINTS = 6

from pynput import keyboard
from enum import Enum

# Initialize numbers
numbers = [60.0, 0.0, 0.0, 60.0, 0.0, 0.0]
numbers_lock = threading.Lock()

calibrate = [60, 0, 0, 60, 0, 0]
home = [10, 0, 0, 10, 0, 0]
# 1->2 unstable (tried: decreasing both hips on 1, increasing and decreasing knee angles, feet decrease)
keypoints = [[90, 126, 67, 90, 126, 67], [90, 126, 66, 74, 107, 90], 
            #[90, 115, 55, 85, 129, 87], 
             [90, 130, 53, 85, 137, 84], [90, 140, 65, 85, 147, 84], 
             [90, 140, 65, 85, 147, 74], [85, 140, 75, 85, 130, 70], 
             
             
             # untested
             [90, 132, 66, 88, 126, 87], 
            [88, 136, 66, 86, 126, 87], [90, 140, 76, 88, 150, 84], 
            [88, 150, 82, 88, 150, 82],
            [90, 126, 66, 90, 126, 66], [73, 108, 90, 90, 126, 66], 
            [73, 126, 84, 90, 126, 66], [88, 126, 84, 90, 126, 66], 
            [88, 126, 84, 90, 136, 66], [88, 150, 84, 90, 140, 76], 
            [88, 150, 82, 88, 150, 82]]

keypoint_num = [-1, 0]
keypoint_lock = threading.Lock()

lower_limits = [0, 0, 0, 0, 0, 0]
upper_limits = [90, 180, 90, 90, 180, 90]
speed = [1, 2, 1, 1, 2, 1]

def to_keypoint(keypoint):
    with numbers_lock:
        deltas = np.array(keypoint) - np.array(numbers)
        max_delta = np.max(np.abs(deltas))
        if max_delta < 4.0:
            return deltas

        speed = 4.0 / max_delta
        # print("numbers:", numbers)
        # print("deltas:", deltas * speed)
        commands = np.round(deltas * speed, decimals=1) + numbers
        # print("current:", commands)
        return commands.tolist()

def at_keypoint(keypoint):
    with numbers_lock:
        deltas = np.array(keypoint) - np.array(numbers)
        max_delta = np.max(np.abs(deltas))
        return max_delta < 1.5

def increment_keypoint(keypoint_num):
    print('called')
    with keypoint_lock:
        keypoint_num[0] += 1

def command_loop():
    print("started!")
    i = 0
    while i < 10000:
        with keypoint_lock:
            print(keypoint_num)
            if keypoint_num[0] == -2:
                send_action(home)
                print(home)
                print("state:", read_state())
            elif keypoint_num[0] == -1:
                send_action(calibrate)
                print(calibrate)
                print("state:", read_state())
            else:
                point = keypoints[keypoint_num[0] % len(keypoints)] 
                print(keypoints[keypoint_num[0] % len(keypoints)] )
                send_action(point)
                print(point)
                print("state:", read_state())
                # if i % 10 == 0:
                #     print(at_keypoint(point))
                #     if at_keypoint(point):
                #         print("press 0 to progress")
                #     print(point, command)
                #     print("state:", read_state())
                # if not at_keypoint(point) and keypoint_num[1] == 0:
                #     with numbers_lock:
                #         # print('here')
                #         for i in range(len(numbers)):
                #             numbers[i] = command[i]
                #         # print(numbers)
                #         send_action(numbers)
        time.sleep(0.2)
        i += 1

    print("finished!")

def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char == '1':
        print('pressed')
        return False
    if key_char == '0':
        print('pressed')
        increment_keypoint(keypoint_num)
    if key_char == '8':
        print('pressed')
        keypoint_num[0] -= 1
    if key_char == '9':
        print('pressed')
        with keypoint_lock:
            keypoint_num[0] = -2

def increment_keypoint(keypoint_num):
    print('called')
    with keypoint_lock:
        keypoint_num[0] += 1

def main():
    open_robot()
    time.sleep(1)
    # 1, 2, 3, 4, 5, 6
    #   1-4
    #   | |
    #   2 5
    #  / /
    # 3 6
    loop_thread = threading.Thread(target=command_loop, daemon=True)
    loop_thread.start()
    # Set up the keyboard listener
    with keyboard.Listener(on_release=on_release, suppress=True) as listener:
        listener.join()


def open_robot():
    global ser
    port_pattern = 'COM5'
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
    byte_array = bytearray([0x41, int(action[0]), int(action[1]), int(action[2]), int(action[3]), int(action[4]), int(action[5]), 0x1])
    ser.write(byte_array)
    # print(f"Wrote: {action[0]} {action[1]} {action[2]} {action[3]} {action[4]} {action[5]}...")

def read_state():
    state = [0.0] * NUM_JOINTS
    global ser
    if ser is None:
        #print("Serial port not open")
        return state
    
    # Keep reading state until we get the last line available
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        numbers = line.split(',')

        # Check line
        if len(numbers) == NUM_JOINTS:
            try:
                # Copy state
                for i in range(NUM_JOINTS):
                    state[i] = numbers[i]
                #print(f"Got: {state}")
            except ValueError:
                print(f"Invalid numbers: {line}")
        else:
            print(f"Invalid line format: {line}")

        # Sleep 
        time.sleep(0.005)

    # Return last read state
    return state

def find_serial_port(pattern):
    ports = glob.glob(pattern)
    if ports:
        return ports[0]
    else:
        raise IOError(f"\n\nNo USB port found: {pattern}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Robot send receive script")
    args = parser.parse_args()
    main()
