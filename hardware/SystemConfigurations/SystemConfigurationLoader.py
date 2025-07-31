import json

from .SystemConfiguration import SystemConfiguration

class SystemConfigurationLoader:
    def load(self) -> SystemConfiguration:
        with open(f"./hardware/SystemConfigurations/system_config.json", 'r') as f:
            system_config_json = json.load(f) # load json from file
        return self._mapper(system_config_json) # use mapper method to convert to usable form
            
    def load_as_dict(self) -> dict:
        return self.load().get_as_dict()

    def _mapper(self, json) -> SystemConfiguration:
        cartridges = json["cartridges"] # get configname data from json
        flow_rate = json["flow_rate_l_s"] # get grid size from json
        start_button_gpio = json["start_button_gpio"]
        stop_button_gpio = json["stop_button_gpio"]
        next_button_gpio = json["next_button_gpio"]
        prev_button_gpio = json["prev_button_gpio"]
        pump1_gpio = json["pump1_gpio"]
        pump2_gpio = json["pump2_gpio"]
        pump3_gpio = json["pump3_gpio"]
        pump4_gpio = json["pump4_gpio"]
        return SystemConfiguration(cartridges, flow_rate, 
                                   start_button_gpio, stop_button_gpio,
                                   next_button_gpio, prev_button_gpio,
                                   pump1_gpio, pump2_gpio, pump3_gpio,
                                   pump4_gpio) # initialise UserConfiguration dataclass with data
