from .UserConfigurations import *
from .SystemConfigurations import *
from flask_socketio import emit

from gpiozero import Button, OutputDevice
import pyautogui
import time
from threading import Timer

class DrinkMachine():
    def __init__(self):
        self.system_config = SystemConfigurationLoader().load()
        self.NUM_CARTRIDGES = self.system_config.get_cartridges()
        print("initialising drink machine")
          
        self.flow_rates = {
            1 : self.system_config.pump1_flow_rate_l_s,
            2 : self.system_config.pump2_flow_rate_l_s,
            3 : self.system_config.pump3_flow_rate_l_s,
            4 : self.system_config.pump4_flow_rate_l_s
        }
        self.isPouring = False
        self.drinkName = None

        self.start_button = Button(self.system_config.start_button_gpio, bounce_time=0.1)
        self.start_button.when_pressed = lambda: pyautogui.hotkey('alt', '1')

        self.stop_button_gpio = Button(self.system_config.stop_button_gpio, bounce_time=0.1)
        self.stop_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', '2')

        self.next_button_gpio = Button(self.system_config.next_button_gpio, bounce_time=0.1)
        self.next_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'w')

        self.prev_button_gpio = Button(self.system_config.prev_button_gpio, bounce_time=0.1)
        self.prev_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'q')

        self.relay_outputs = [
            OutputDevice(self.system_config.pump1_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump2_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump3_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump4_gpio, active_high=True, initial_value=False)
        ]

        self.active_timers = []

    def test_socket(self):
        emit("pour_state", self.get_state(), broadcast=True, namespace="/")

    def get_state(self):
        return {
            "active" : self.isPouring,
            "drink" : self.drinkName,
            "progress" : self.get_progress()
        }
    
    def get_progress(self):
        if not self.active_timers:
            return 0.0

        # take the "longest" active timer (drink progress is tied to the slowest component)
        longest = max(self.active_timers, key=lambda t: t["duration"])
        elapsed = time.time() - longest["start"]

        progress = min(elapsed / longest["duration"], 1.0)  # clamp 0–1
        return progress
    
    def relayOff(self, relay):
        relay.off()
        # remove finished timer
        self.active_timers = [t for t in self.active_timers if t["relay"] != relay]
        if not self.active_timers:   # all pouring finished
            self.isPouring = False
            self.drinkName = None
            emit("pour_state", self.get_state(), broadcast=True, namespace="/")  # <-- works!

    def activate_relay(self, relay, duration):
        relay.on()
        start_time = time.time()
        timer = Timer(duration, lambda : self.relayOff(relay))
        timer.start()

        self.active_timers.append({
            "relay": relay,
            "timer": timer,
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
            self.activate_relay(self.relay_outputs[int(cartridge_no)-1], time_s)

    def stop(self):
        # Cancel all timers
        for timer in self.active_timers:
            timer.cancel()
        self.active_timers.clear()

        self.isPouring = False
        self.drinkName = None

        # Turn off all relays
        for relay in self.relay_outputs:
            relay.off()
        
        emit("pour_state", self.get_state(), broadcast=True, namespace="/")
