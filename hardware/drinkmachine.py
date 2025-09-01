from threading import Timer
from .UserConfigurations import *
from .SystemConfigurations import *
from flask_socketio import emit, SocketIO
from gpiozero import Button, OutputDevice
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
          
        self.flow_rates = {
            1: self.system_config.pump1_flow_rate_l_s,
            2: self.system_config.pump2_flow_rate_l_s,
            3: self.system_config.pump3_flow_rate_l_s,
            4: self.system_config.pump4_flow_rate_l_s
        }
        self.isPouring = False
        self.drinkName = None

        # Buttons → send hotkeys
        self.start_button = Button(self.system_config.start_button_gpio, bounce_time=0.1)
        self.start_button.when_pressed = lambda: pyautogui.hotkey('alt', '1')

        self.stop_button_gpio = Button(self.system_config.stop_button_gpio, bounce_time=0.1)
        self.stop_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', '2')

        self.next_button_gpio = Button(self.system_config.next_button_gpio, bounce_time=0.1)
        self.next_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'w')

        self.prev_button_gpio = Button(self.system_config.prev_button_gpio, bounce_time=0.1)
        self.prev_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'q')

        # Relay outputs
        self.relay_outputs = [
            OutputDevice(self.system_config.pump1_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump2_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump3_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump4_gpio, active_high=True, initial_value=False)
        ]

        # Track active pours
        self.active_relays = []  # each: {relay, start, duration}

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
            return 0.0

        # progress is tied to the slowest component
        longest = max(self.active_relays, key=lambda t: t["duration"])
        elapsed = time.time() - longest["start"]
        return min(elapsed / longest["duration"], 1.0)  # clamp 0–1
    
    def activate_relay(self, relay, duration):
        def relayOff():
            relay.off()
            # remove finished relay from active list
            self.active_relays = [t for t in self.active_relays if t["relay"] != relay]
            if not self.active_relays:   # all pouring finished
                self.isPouring = False
                self.drinkName = None
                self.socketio.emit("pour_state", self.get_state())

        relay.on()
        start_time = time.time()
        self.active_relays.append({
            "relay": relay,
            "start": start_time,
            "duration": duration
        })
        # async background task replaces threading.Timer
        Timer(duration, relayOff)

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
            self.activate_relay(self.relay_outputs[int(cartridge_no) - 1], time_s)

    def stop(self):
        # Immediately stop everything
        for relay in self.relay_outputs:
            relay.off()
        self.active_relays.clear()
        self.isPouring = False
        self.drinkName = None

        self.socketio.emit("pour_state", self.get_state())
