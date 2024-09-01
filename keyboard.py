from pynput import keyboard
from enum import Enum

# Initialize numbers
numbers = [0, 0, 0, 0, 0, 0]

# Define key mappings for increasing and decreasing
increase_keys = {'q', 'w', 'e', 'r', 't', 'y'}
decrease_keys = {'a', 's', 'd', 'f', 'g', 'h'}
multi_keys_up = {'z', 'x'}
multi_keys_down = {'v', 'c'}

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
numbers = [0, 0, 0, 0, 0, 0]
lower_limits = [0, 0, 0, 0, 0, 0]
upper_limits = [20, 180, 90, 20, 180, 90]

# Track currently pressed keys
pressed_keys = set()

def on_press(key):
    try:
        key_char = key.char
        print(int(key_char) - 2)
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char in increase_keys or key_char in decrease_keys or key_char in multi_keys_up or key_char in multi_keys_down:
        pressed_keys.add(key_char)
        update_numbers(numbers)

def on_release(key):
    try:
        key_char = key.char
    except AttributeError:
        # Handle special keys if needed
        return

    if key_char == '1':
        return False

    if key_char in pressed_keys:
        pressed_keys.remove(key_char)
        update_numbers(numbers)

def update_numbers(numbers):
    for key in pressed_keys:
        if key in increase_keys:
            index = key_to_index[key]
            if numbers[index] < upper_limits[index]:
                numbers[index] += 0.5
        elif key in decrease_keys:
            index = key_to_index[key]
            if numbers[index] > lower_limits[index]:
                numbers[index] -= 0.5
        elif key in multi_keys_up:
            index = key_to_index[key]
            if numbers[index] < upper_limits[index]:
                numbers[index] += 0.5
            if numbers[index + 3] < upper_limits[index]:
                numbers[index + 3] += 0.5
        else:
            index = key_to_index[key]
            if numbers[index] > upper_limits[index]:
                numbers[index] -= 0.5
            if numbers[index + 3] > upper_limits[index]:
                numbers[index + 3] -= 0.5

    
    for i in range(len(numbers)):
        numbers[i] = round(numbers[i], 1)

    print(f'Numbers: {numbers}')

def main():
    # Set up the keyboard listener
    with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True) as listener:
        listener.join()

if __name__ == '__main__':
    main()