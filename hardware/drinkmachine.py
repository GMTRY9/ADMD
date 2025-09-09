import RPi.GPIO as GPIO
from threading import Timer
from .UserConfigurations import *
from .SystemConfigurations import *
from flask_socketio import emit, SocketIO
import pyautogui
import time
import traceback


class DrinkMachine():
    def __init__(self):
        self.socketio = None

        self.system_config = SystemConfigurationLoader().load()
        self.NUM_CARTRIDGES = self.system_config.get_cartridges()
        print("initialising drink machine")
        print("DrinkMachine init", self)
        traceback.print_stack(limit=3)

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)  # Use BCM numbering
        GPIO.setwarnings(False)

        # Flow rates from config
        self.flow_rates = {
            1: self.system_config.pump1_flow_rate_l_s,
            2: self.system_config.pump2_flow_rate_l_s,
            3: self.system_config.pump3_flow_rate_l_s,
            4: self.system_config.pump4_flow_rate_l_s
        }
        self.isPouring = False
        self.drinkName = None

        # Buttons setup
        self._setup_button(self.system_config.start_button_gpio, lambda: pyautogui.hotkey('alt', '1'))
        self._setup_button(self.system_config.stop_button_gpio, lambda: pyautogui.hotkey('alt', '2'))
        self._setup_button(self.system_config.next_button_gpio, lambda: pyautogui.hotkey('alt', 'w'))
        self._setup_button(self.system_config.prev_button_gpio, lambda: pyautogui.hotkey('alt', 'q'))

        # Relay outputs setup
        self.relay_pins = [
            self.system_config.pump1_gpio,
            self.system_config.pump2_gpio,
            self.system_config.pump3_gpio,
            self.system_config.pump4_gpio
        ]
        for pin in self.relay_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        # Track active pours
        self.active_relays = []  # each: {pin, start, duration}

    def _setup_button(self, pin, callback):
        """Setup a GPIO input with falling edge detection and callback."""
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=lambda channel: callback(), bouncetime=100)

    def set_socketio(self, socketio):
        self.socketio = socketio

    def test_socket(self):
        self.socketio.emit("pour_state", self.get_state())

    def get_state(self):
        return {
            "active": self.isPouring,
            "drink": self.drinkName,
            "progress": self.get_progress()
        }

    def get_progress(self):
        if not self.active_relays:
            return 0

        # progress is tied to the slowest component
        longest = max(self.active_relays, key=lambda t: t["duration"])

        if longest["duration"] <= 0:
            return 1.0  # treat as "done" if duration is invalid

        elapsed = time.time() - longest["start"]
        return min(elapsed / longest["duration"], 1.0)  # clamp 0–1

    def activate_relay(self, pin, duration):
        def relayOff():
            GPIO.output(pin, GPIO.LOW)
            # remove finished relay from active list
            self.active_relays = [t for t in self.active_relays if t["pin"] != pin]
            if not self.active_relays:   # all pouring finished
                self.isPouring = False
                self.drinkName = None
                self.socketio.emit("pour_state", self.get_state())

        GPIO.output(pin, GPIO.HIGH)
        start_time = time.time()
        timer = Timer(duration, relayOff)
        timer.start()
        self.active_relays.append({
            "pin": pin,
            "start": start_time,
            "duration": duration
        })

    def start(self, config_index):
        config = UserConfigurationLoader(str(config_index)).load()
        print(config.proportions)

        if self.isPouring:
            return False

        self.isPouring = True
        self.drinkName = config.get_name()

        for cartridge_no, volume_ml in config.proportions.items():
            volume_l = volume_ml / 1000
            time_s = volume_l / self.flow_rates[int(cartridge_no)]
            pin = self.relay_pins[int(cartridge_no) - 1]
            self.activate_relay(pin, time_s)

    def stop(self):
        # Immediately stop everything
        for pin in self.relay_pins:
            GPIO.output(pin, GPIO.LOW)
        self.active_relays.clear()
        self.isPouring = False
        self.drinkName = None

        self.socketio.emit("pour_state", self.get_state())

    def cleanup(self):
        GPIO.cleanup()
