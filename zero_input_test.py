from gpiozero import Button
from signal import pause

# Callbacks
def start_response():
    print("start pressed")

def stop_response():
    print("stop pressed")

def next_response():
    print("next pressed")

def prev_response():
    print("prev pressed")

# GPIO pin numbers (BCM)
stop_button_gpio = 15
start_button_gpio = 18
next_button_gpio = 14
prev_button_gpio = 23

# Setup buttons (active high, since pressed = 3.3V)
stop_button = Button(stop_button_gpio, pull_up=False, bounce_time=0.4)
start_button = Button(start_button_gpio, pull_up=False, bounce_time=0.4)
next_button = Button(next_button_gpio, pull_up=False, bounce_time=0.4)
prev_button = Button(prev_button_gpio, pull_up=False, bounce_time=0.4)

# Assign callbacks (on_press)
stop_button.when_pressed = stop_response
start_button.when_pressed = start_response
next_button.when_pressed = next_response
prev_button.when_pressed = prev_response

# Keep the script alive
pause()
