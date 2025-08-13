from .UserConfigurations import *
from .SystemConfigurations import *

from gpiozero import Button, OutputDevice
import pyautogui
from threading import Timer

class DrinkMachine():
    def __init__(self):
        self.system_config = SystemConfigurationLoader().load()
        self.NUM_CARTRIDGES = self.system_config.get_cartridges()
        self.FLOW_RATE = self.system_config.flow_rate_l_s
        self.isPouring = False

        # self.start_button = Button(self.system_config.start_button_gpio, bounce_time=0.1)
        # self.start_button.when_pressed = lambda: pyautogui.hotkey('alt', '1')

        # self.stop_button_gpio = Button(self.system_config.stop_button_gpio, bounce_time=0.1)
        # self.stop_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', '2')

        # self.next_button_gpio = Button(self.system_config.next_button_gpio, bounce_time=0.1)
        # self.next_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'w')

        # self.prev_button_gpio = Button(self.system_config.prev_button_gpio, bounce_time=0.1)
        # self.prev_button_gpio.when_pressed = lambda: pyautogui.hotkey('alt', 'q')

        self.relay_outputs = [
            # OutputDevice(self.system_config.pump1_gpio, active_high=True, initial_value=False),
            # OutputDevice(self.system_config.pump2_gpio, active_high=True, initial_value=False),
            # OutputDevice(self.system_config.pump3_gpio, active_high=True, initial_value=False),
            # OutputDevice(self.system_config.pump4_gpio, active_high=True, initial_value=False)
        ]

        self.active_timers = []

    def activate_relay(self, relay, duration):
        relay.on()
        timer = Timer(duration, relay.off)
        timer.start()
        self.active_timers.append(timer)

    def start(self, config_index):
        config = UserConfigurationLoader(str(config_index)).load()
    
        print(config.proportions)

        if self.isPouring:
            return
        
        self.isPouring = True
        for cartridge_no, volume_ml in config.proportions.items():
            volume_l = volume_ml / 1000
            time_s = volume_l / self.FLOW_RATE
            self.activate_relay(self.relay_outputs[int(cartridge_no)-1], time_s)
        
        self.isPouring = False

    def stop(self):
        # Cancel all timers
        for timer in self.active_timers:
            timer.cancel()
        self.active_timers.clear()

        self.isPouring = False

        # Turn off all relays
        for relay in self.relay_outputs:
            relay.off()
