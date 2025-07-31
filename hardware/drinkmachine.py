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

        self.start_button = Button(self.system_config.start_button_gpio)
        self.start_button.when_pressed = lambda: pyautogui.hotkey('ctrl', 'alt', 's')

        self.stop_button_gpio = Button(self.system_config.stop_button_gpio)
        self.stop_button_gpio.when_pressed = lambda: pyautogui.hotkey('ctrl', 'alt', 'x')

        self.next_button_gpio = Button(self.system_config.next_button_gpio)
        self.next_button_gpio.when_pressed = lambda: pyautogui.hotkey('ctrl', 'alt', 'right')

        self.prev_button_gpio = Button(self.system_config.prev_button_gpio)
        self.prev_button_gpio.when_pressed = lambda: pyautogui.hotkey('ctrl', 'alt', 'left')

        self.relay_outputs = [
            OutputDevice(self.system_config.pump1_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump2_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump3_gpio, active_high=True, initial_value=False),
            OutputDevice(self.system_config.pump4_gpio, active_high=True, initial_value=False)
        ]

        self.active_timers = []

    def activate_relay(self, relay, duration):
        relay.on()
        timer = Timer(duration, relay.off)
        timer.start()
        self.active_timers.append(timer)

    def start(self, config_index):
        config = UserConfigurationLoader(str(config_index)).load()
        self.stop() 
        for cartridge_no, volume_ml in config.proportions.values():
            volume_l = volume_ml / 1000
            time_s = volume_l / self.FLOW_RATE
            self.activate_relay(self.relay_outputs[cartridge_no-1], time_s)

    def stop(self):
        # Cancel all timers
        for timer in self.active_timers:
            timer.cancel()
        self.active_timers.clear()

        # Turn off all relays
        for relay in self.relay_outputs:
            relay.off()
