import json

from .SystemConfiguration import SystemConfiguration

class SystemConfigurationLoader:
    def load(self) -> SystemConfiguration:
        with open(f"./system_config.json", 'r') as f:
            system_config_json = json.load(f) # load json from file
        return self._mapper(system_config_json) # use mapper method to convert to usable form
            
    def load_as_dict(self) -> dict:
        return self.load().get_as_dict()

    def _mapper(self, json) -> SystemConfiguration:
        cartridges = json["cartridges"] # get configname data from json
        start_button_gpio = json["start_button_gpio"]
        stop_button_gpio = json["stop_button_gpio"]
        next_button_gpio = json["next_button_gpio"]
        prev_button_gpio = json["prev_button_gpio"]
        pump1_gpio = json["pump1_gpio"]
        pump1_flow_rate_l_s = json["pump1_flow_rate_l_s"]
        pump2_gpio = json["pump2_gpio"]
        pump2_flow_rate_l_s = json["pump2_flow_rate_l_s"]
        pump3_gpio = json["pump3_gpio"]
        pump3_flow_rate_l_s = json["pump3_flow_rate_l_s"]
        pump4_gpio = json["pump4_gpio"]
        pump4_flow_rate_l_s = json["pump4_flow_rate_l_s"]
        return SystemConfiguration(cartridges,
                                   start_button_gpio, stop_button_gpio,
                                   next_button_gpio, prev_button_gpio,
                                   pump1_gpio, pump1_flow_rate_l_s, 
                                   pump2_gpio, pump2_flow_rate_l_s, 
                                   pump3_gpio, pump3_flow_rate_l_s,
                                   pump4_gpio, pump4_flow_rate_l_s,) # initialise UserConfiguration dataclass with data
