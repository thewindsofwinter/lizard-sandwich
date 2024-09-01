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
numbers = [10.0, 0.0, 0.0, 10.0, 0.0, 0.0]
numbers_lock = threading.Lock()
keypoints = [[50, 0, 0, 50, 0, 0], [90.0, 96.0, 48.0, 90.0, 96.0, 48.0], [90.0, 96.0, 48.0, 70.0, 96.0, 68.0], 
            [90.0, 134.0, 48.0, 70.0, 134.0, 68.0], [78.0, 124.5, 55.5, 70.0, 134.0, 59.5], 
            [70.0, 134.0, 59.0, 70.0, 134.0, 59.0]]
keypoint_num = [0, 1]
keypoint_lock = threading.Lock()

# Define key mappings for increasing and decreasing
increase_keys = {'q', 'w', 'e', 'r', 't', 'y'}
decrease_keys = {'a', 's', 'd', 'f', 'g', 'h'}
multi_keys_up = {'z', 'x'}
multi_keys_down = {'v', 'c'}
match_keys = {'2', '3', '4', '5', '6', '7'}

class Joint(Enum):
    LEFT_HIP = 0
    RIGHT_HIP = 3
    LEFT_KNEE = 1
    RIGHT_KNEE = 4
    LEFT_FOOT = 2
    RIGHT_FOOT = 5

# Define the corresponding index for each key
key_to_index = {
    'q': Joint.LEFT_FOOT.value, 'w': Joint.RIGHT_FOOT.value, 'e': Joint.LEFT_KNEE.value, 'r': Joint.RIGHT_KNEE.value, 't': Joint.LEFT_HIP.value, 'y': Joint.RIGHT_HIP.value,
    'a': Joint.LEFT_FOOT.value, 's': Joint.RIGHT_FOOT.value, 'd': Joint.LEFT_KNEE.value, 'f': Joint.RIGHT_KNEE.value, 'g': Joint.LEFT_HIP.value, 'h': Joint.RIGHT_HIP.value,
    'z': Joint.LEFT_KNEE.value, 'x': Joint.LEFT_FOOT.value, 'c': Joint.LEFT_KNEE.value, 'v': Joint.LEFT_FOOT.value
}

# 1, 2, 3, 4, 5, 6 (except minus 1 for joints)
#   1-4
#   | |
#   2 5
#  / /
# 3 6
lower_limits = [0, 0, 0, 0, 0, 0]
upper_limits = [90, 180, 90, 90, 180, 90]
speed = [1, 2, 1, 1, 2, 1]

# Track currently pressed keys
pressed_keys = set()

def to_keypoint(keypoint):
    with numbers_lock:
        deltas = np.array(keypoint) - np.array(numbers)
        max_delta = np.max(np.abs(deltas))
        if max_delta < 0.5:
            return deltas

        speed = 0.5 / max_delta
        print("numbers:", numbers)
        print("deltas:", deltas * speed)
        commands = np.round(deltas * speed, decimals=1) + numbers
        print("current:", commands)
        return commands.tolist()

def at_keypoint(keypoint):
    with numbers_lock:
        deltas = np.array(keypoint) - np.array(numbers)
        max_delta = np.max(np.abs(deltas))
        return max_delta < 0.5

def on_press(key):
    try:
        key_char = key.char
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char in increase_keys or key_char in decrease_keys or key_char in multi_keys_up or key_char in multi_keys_down or key_char in match_keys:
        pressed_keys.add(key_char)
        update_numbers()

def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char == '1':
        return False
    if key_char == '0':
        print('pressed')
        increment_keypoint(keypoint_num)
    if key_char == '9':
        with keypoint_lock:
            keypoint_num[1] = 1 - keypoint_num[1]

    if key_char in pressed_keys:
        pressed_keys.remove(key_char)
        update_numbers()

def increment_keypoint(keypoint_num):
    print('called')
    with keypoint_lock:
        keypoint_num[0] += 1

def update_numbers():
    with numbers_lock:
        for key in pressed_keys:
            if key in increase_keys:
                index = key_to_index[key]
                if numbers[index] < upper_limits[index]:
                    numbers[index] += 0.5 * speed[index]
            elif key in decrease_keys:
                index = key_to_index[key]
                if numbers[index] > lower_limits[index]:
                    numbers[index] -= 0.5 * speed[index]
            elif key in multi_keys_up:
                index = key_to_index[key]
                if numbers[index] < upper_limits[index]:
                    numbers[index] += 0.5 * speed[index]
                if numbers[index + 3] < upper_limits[index]:
                    numbers[index + 3] += 0.5 * speed[index]
            elif key in multi_keys_down:
                index = key_to_index[key]
                # print(key, key_to_index[key])
                if numbers[index] > lower_limits[index]:
                    numbers[index] -= 0.5 * speed[index]
                if numbers[index + 3] > lower_limits[index]:
                    numbers[index + 3] -= 0.5 * speed[index]
            else:
                match = int(key) - 2
                print(match)
                to_match = match + 3
                if match >= 3:
                    to_match = match - 3
                
                if numbers[to_match] > numbers[match]:
                    numbers[match] += 0.5 * speed[match]
                elif numbers[to_match] < numbers[match]:
                    numbers[match] -= 0.5 * speed[match]

        
        for i in range(len(numbers)):
            numbers[i] = round(numbers[i], 1)

    # print(pressed_keys)
    # print(f'Command changed to: {numbers}')

def command_loop():
    print("started!")
    i = 0
    while i < 10000:
        with keypoint_lock:
            if i % 10 == 0:
                 print(i, numbers)
                 print(read_state())
            send_action(numbers)
            #point = keypoints[keypoint_num[0]]
            #command = to_keypoint(point)
            #if i % 10 == 0:
            #    print(at_keypoint(point))
            #    print(point, command)
            #if not at_keypoint(point) and keypoint_num[1] == 0:
            #    with numbers_lock:
            #        # print('here')
            #        for i in range(len(numbers)):
            #            numbers[i] = command[i]
            #        # print(numbers)
            #        send_action(numbers)
            #else:
            #    #with numbers_lock:
            #    #    print(numbers)
            #    #    send_action(numbers)
        time.sleep(0.1)
        i += 1

    print("finished!")

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
    with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
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
    print(f"Wrote: {action[0]} {action[1]} {action[2]} {action[3]} {action[4]} {action[5]}...")

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
