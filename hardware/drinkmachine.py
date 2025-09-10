from gpiozero import Button, OutputDevice
from threading import Timer
from .UserConfigurations import *
from .SystemConfigurations import *
from flask_socketio import emit, SocketIO
import pyautogui
import time
import traceback


class PourScheduler:
    def __init__(self, relays, flow_rates, socketio=None, max_active=3, min_chunk=1.0, chunks_per_pump=3):
        self.relays = relays
        self.flow_rates = flow_rates
        self.socketio = socketio
        self.max_active = max_active
        self.min_chunk = min_chunk
        self.chunks_per_pump = chunks_per_pump

        self.active_relays = []  # {relay, start, duration, timer}
        self.plan = []
        self.is_running = False
        self.drink_name = None

    def _relay_off(self, relay):
        relay.off()
        self.active_relays = [t for t in self.active_relays if t["relay"] != relay]

        if self.socketio:
            self.socketio.emit("pour_state", self.get_state())

    def _activate_relay(self, relay, duration):
        def relay_off():
            self._relay_off(relay)

        relay.on()
        start_time = time.time()
        timer = Timer(duration, relay_off)
        timer.start()

        self.active_relays.append({
            "relay": relay,
            "start": start_time,
            "duration": duration,
            "timer": timer,
        })

    def _run_step(self, index):
        if index >= len(self.plan):
            # finished
            self.is_running = False
            self.drink_name = None
            if self.socketio:
                self.socketio.emit("pour_state", self.get_state())
            return

        relay, dur = self.plan[index]

        # enforce max active relays
        if len(self.active_relays) >= self.max_active:
            Timer(0.2, lambda: self._run_step(index)).start()
            return

        self._activate_relay(relay, dur)

        # schedule next step with a slight overlap
        Timer(dur * 0.9, lambda: self._run_step(index + 1)).start()

        if self.socketio:
            self.socketio.emit("pour_state", self.get_state())

    def start(self, proportions, drink_name):
        if self.is_running:
            return False

        self.active_relays = []
        self.is_running = True
        self.drink_name = drink_name

        # build pour plan
        pour_plan = []
        for cartridge_no, volume_ml in proportions.items():
            if not volume_ml:
                continue
            volume_l = volume_ml / 1000
            total_time = volume_l / self.flow_rates[int(cartridge_no)]
            relay = self.relays[int(cartridge_no) - 1]

            chunk_time = max(self.min_chunk, total_time / self.chunks_per_pump)
            remaining = total_time
            while remaining > 0:
                dur = min(chunk_time, remaining)
                pour_plan.append((relay, dur))
                remaining -= dur

        # interleave plan for mixing
        interleaved = []
        while pour_plan:
            seen_relays = set()
            for step in pour_plan[:]:
                relay, dur = step
                if relay in seen_relays:
                    continue
                interleaved.append(step)
                pour_plan.remove(step)
                seen_relays.add(relay)

        self.plan = interleaved
        self._run_step(0)
        return True

    def stop(self):
        for t in self.active_relays:
            if "timer" in t:
                t["timer"].cancel()
        for relay in self.relays:
            relay.off()
        self.active_relays = []
        self.plan = []
        self.is_running = False
        self.drink_name = None

        if self.socketio:
            self.socketio.emit("pour_state", self.get_state())

    def get_progress(self):
        if not self.active_relays and not self.plan:
            return 1.0 if not self.is_running else 0.0
        if not self.active_relays:
            return 0.0

        longest = max(self.active_relays, key=lambda t: t["duration"])
        elapsed = time.time() - longest["start"]
        return min(elapsed / longest["duration"], 1.0)

    def get_state(self):
        return {
            "active": self.is_running,
            "drink": self.drink_name,
            "progress": self.get_progress(),
        }


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

        # --- Button setup ---
        try:
            self.stop_button = Button(self.system_config.stop_button_gpio,
                                      pull_up=False, bounce_time=0.07)
            self.start_button = Button(self.system_config.start_button_gpio,
                                       pull_up=False, bounce_time=0.07)
            self.next_button = Button(self.system_config.next_button_gpio,
                                      pull_up=False, bounce_time=0.07)
            self.prev_button = Button(self.system_config.prev_button_gpio,
                                      pull_up=False, bounce_time=0.07)

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
        except:
            print("WARNING: GPIO not detected")
            self.relays = []

        # Pour scheduler
        self.scheduler = PourScheduler(
            relays=self.relays,
            flow_rates=self.flow_rates,
            socketio=self.socketio,
            max_active=3,
            min_chunk=1.0,
            chunks_per_pump=3,
        )

    def _press_hotkey(self, key1, key2):
        print(f"pressing {key1} + {key2}")
        pyautogui.hotkey(key1, key2)

    def set_socketio(self, socketio):
        self.socketio = socketio
        self.scheduler.socketio = socketio

    def test_socket(self):
        if self.socketio:
            self.socketio.emit("pour_state", self.get_state())

    def get_state(self):
        return self.scheduler.get_state()

    def get_progress(self):
        return self.scheduler.get_progress()

    def start(self, config_index):
        config = UserConfigurationLoader(str(config_index)).load()
        print(config.proportions)
        return self.scheduler.start(config.proportions, config.get_name())

    def stop(self):
        self.scheduler.stop()

    def cleanup(self):
        self.scheduler.stop()
        for relay in self.relays:
            relay.off()
        # gpiozero cleans itself up automatically
