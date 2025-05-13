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
        return SystemConfiguration(cartridges, flow_rate) # initialise UserConfiguration dataclass with data
