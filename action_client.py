#!/usr/bin/env python3
import serial
import time
import glob
import argparse
import threading
import numpy as np
from enum import Enum

# USB port
ser = None
NUM_JOINTS = 6

from pynput import keyboard

class Mode(Enum):
    NEUTRAL = -1
    SIT = 0
    STAND = 1
    STEP = 2
    STEP_CONTINUOUS = 3
    HIP_UP = 3
    HIP_DOWN = 4

calibrate = [60, 0, 0, 60, 0, 0]
standing = [90, 126, 66, 90, 126, 66]

one_step = [[90, 126, 66, 90, 126, 66], [90, 126, 66, 90, 116, 66], [90, 126, 66, 70, 108, 86], 
             [90, 130, 53, 85, 137, 84], [90, 140, 64, 85, 147, 84], [90, 137, 66, 85, 135, 74],
             [90, 129, 54, 85, 126, 62], [85, 126, 62, 85, 126, 62], [70, 30, 15, 70, 30, 15]]

keypoint_num = [-1]
keypoint_lock = threading.Lock()

mode = Mode.NEUTRAL
mode_lock = threading.Lock()

lower_limits = [0, 0, 0, 0, 0, 0]
upper_limits = [100, 180, 90, 100, 180, 90]
speed = [1, 2, 1, 1, 2, 1]

def at_keypoint(keypoint):
    deltas = np.array(keypoint) - np.array(read_state())
    max_delta = np.max(np.abs(deltas))
    return max_delta < 0.3

def increment_keypoint(keypoint_num):
    print('called')
    with keypoint_lock:
        keypoint_num[0] += 1

def get_mode():
    with mode_lock:
        return mode[0]

def command_loop():
    print("started!")
    i = 0
    while i < 10000:
        with mode_lock:
            if mode[0] == Mode.NEUTRAL:
                pass
            elif mode[0] == Mode.SIT:
                send_action(calibrate)
                print(calibrate)
                print("state:", read_state())
            elif mode[0] == Mode.STAND:
                send_action(standing)
                print(standing)
                print("state:", read_state())
            elif mode[0] == Mode.STEP:
                with keypoint_lock:
                    if keypoint_num[0] == -1:
                        if at_keypoint(calibrate):
                            keypoint_num[0] += 1
                            continue
                            
                        send_action(calibrate)
                        print(calibrate)
                        print("state:", read_state())
                    else:
                        point = one_step[keypoint_num[0] % len(one_step)] 
                        if (keypoint_num[0] // len(one_step)) % 2 == 1:
                            point = [point[3], point[4], point[5], point[0], point[1], point[2]]
                            
                        if at_keypoint(point):                    
                            if keypoint_num[0] == len(one_step):
                                keypoint_num[0] = -1
                                mode[0] = Mode.STAND
                            else:
                                keypoint_num[0] += 1
                            continue

                        send_action(point)
                        print(point)
                        print("state:", read_state())
            elif mode[0] == Mode.STEP_CONTINUOUS:
                with keypoint_lock:
                    if keypoint_num[0] == -1:
                        if at_keypoint(calibrate):
                            keypoint_num[0] += 1
                            continue
                            
                        send_action(calibrate)
                        print(calibrate)
                        print("state:", read_state())
                    else:
                        point = one_step[keypoint_num[0] % len(one_step)] 
                        if (keypoint_num[0] // len(one_step)) % 2 == 1:
                            point = [point[3], point[4], point[5], point[0], point[1], point[2]]
                            
                        if at_keypoint(point):
                            keypoint_num[0] += 1
                            continue

                        send_action(point)
                        print(point)
                        print("state:", read_state())
            elif mode[0] == Mode.HIP_UP:
                status = read_state()
                if status[0] < upper_limits - 10 and status[1] < upper_limits - 10:
                    status[0] += 10
                    status[3] += 10
                    send_action(status)
                    mode[0] = Mode.STAND
            elif mode == Mode.HIP_DOWN:
                status = read_state()
                if status[0] > lower_limits + 10 and status[1] > lower_limits + 10:
                    status[0] -= 10
                    status[3] -= 10
                    send_action(status)
                    mode[0] = Mode.STAND
        time.sleep(0.2)
        i += 1

    print("finished!")

def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char == 't':
        print('terminating')
        return False
    if key_char == 'h':
        with mode_lock:
            mode[0] = Mode.SIT
        with keypoint_lock:
            keypoint_num[0] = -1

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
                    state[i] = float(numbers[i])
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
