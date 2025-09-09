from signal import pause
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # Use BCM numbering
GPIO.setwarnings(False)

def start_response():
    print("start pressed")

def stop_response():
    print("stop pressed")

def next_response():
    print("next pressed")

def prev_response():
    print("prev pressed")

def _setup_button(pin, callback):
    """Setup a GPIO input with falling edge detection and callback."""
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=400)

stop_button_gpio = 15
start_button_gpio = 18
next_button_gpio = 14
prev_button_gpio = 23

# Buttons setup
_setup_button(stop_button_gpio, stop_response)
_setup_button(start_button_gpio, start_response)
_setup_button(next_button_gpio, next_response)
_setup_button(prev_button_gpio, prev_response)

input()

GPIO.cleanup()
