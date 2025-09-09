from gpiozero import Button, OutputDevice
from threading import Timer
from .UserConfigurations import *
from .SystemConfigurations import *
from flask_socketio import emit, SocketIO
import pyautogui
import time
import traceback


class DrinkMachine:
    def __init__(self):
        self.socketio = None
        self.system_config = SystemConfigurationLoader().load()
        self.NUM_CARTRIDGES = self.system_config.get_cartridges()
        print("initialising drink machine")
        print("DrinkMachine init", self)
        traceback.print_stack(limit=3)

        # Flow rates from config
        self.flow_rates = {
            1: self.system_config.pump1_flow_rate_l_s,
            2: self.system_config.pump2_flow_rate_l_s,
            3: self.system_config.pump3_flow_rate_l_s,
            4: self.system_config.pump4_flow_rate_l_s,
        }

        self.isPouring = False
        self.drinkName = None
        self.active_relays = []  # each: {pin, start, duration}

        # --- Button setup ---
        # active_high=True, pull_up=False since wiring = 3.3V press with pulldown
        self.stop_button = Button(self.system_config.stop_button_gpio,
                                  pull_up=False, bounce_time=0.4)
        self.start_button = Button(self.system_config.start_button_gpio,
                                   pull_up=False, bounce_time=0.4)
        self.next_button = Button(self.system_config.next_button_gpio,
                                  pull_up=False, bounce_time=0.4)
        self.prev_button = Button(self.system_config.prev_button_gpio,
                                  pull_up=False, bounce_time=0.4)

        # Map button actions
        self.stop_button.when_pressed = lambda: self._press_hotkey("alt", "2")
        self.start_button.when_pressed = lambda: self._press_hotkey("alt", "1")
        self.next_button.when_pressed = lambda: self._press_hotkey("alt", "w")
        self.prev_button.when_pressed = lambda: self._press_hotkey("alt", "q")

        # --- Relay setup ---
        self.relay_pins = [
            self.system_config.pump1_gpio,
            self.system_config.pump2_gpio,
            self.system_config.pump3_gpio,
            self.system_config.pump4_gpio,
        ]
        self.relays = [OutputDevice(pin, active_high=True, initial_value=False)
                       for pin in self.relay_pins]

    def _press_hotkey(self, key1, key2):
        print(f"pressing {key1} + {key2}")
        pyautogui.hotkey(key1, key2)

    def set_socketio(self, socketio):
        self.socketio = socketio

    def test_socket(self):
        self.socketio.emit("pour_state", self.get_state())

    def get_state(self):
        return {
            "active": self.isPouring,
            "drink": self.drinkName,
            "progress": self.get_progress(),
        }

    def get_progress(self):
        if not self.active_relays:
            return 0

        longest = max(self.active_relays, key=lambda t: t["duration"])
        if longest["duration"] <= 0:
            return 1.0

        elapsed = time.time() - longest["start"]
        return min(elapsed / longest["duration"], 1.0)

    def activate_relay(self, relay: OutputDevice, duration: float):
        def relay_off():
            relay.off()
            self.active_relays = [t for t in self.active_relays if t["relay"] != relay]
            if not self.active_relays:
                self.isPouring = False
                self.drinkName = None
                self.socketio.emit("pour_state", self.get_state())

        relay.on()
        start_time = time.time()
        timer = Timer(duration, relay_off)
        timer.start()
        self.active_relays.append({
            "relay": relay,
            "start": start_time,
            "duration": duration,
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
            relay = self.relays[int(cartridge_no) - 1]
            time.sleep(0.1)
            self.activate_relay(relay, time_s)

    def stop(self):
        # Immediately stop all pumps
        for relay in self.relays:
            relay.off()
        self.active_relays.clear()
        self.isPouring = False
        self.drinkName = None
        if self.socketio:
            self.socketio.emit("pour_state", self.get_state())

    def cleanup(self):
        for relay in self.relays:
            relay.off()
        # gpiozero cleans itself up automatically
