import json

from .UserConfiguration import UserConfiguration

class UserConfigurationLoader:
    def __init__(self, name : str):
        self.name = name
    
    def load(self) -> UserConfiguration:
        with open(f"./hardware/UserConfigurations/Data/{self.name}.json", 'r') as f:
            user_config_json = json.load(f) # load json from file
        return self._mapper(user_config_json) # use mapper method to convert to usable form
            
    def load_as_dict(self) -> dict:
        return self.load().get_as_dict()

    def _mapper(self, json) -> UserConfiguration:
        name = json["name"] # get configname data from json
        proportions = json["proportions"] # get grid size from json
        default_size = json["default_size"]
        return UserConfiguration(name, proportions, default_size) # initialise UserConfiguration dataclass with data
