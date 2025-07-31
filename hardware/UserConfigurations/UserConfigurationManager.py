from os import listdir, remove

from .UserConfigurationSaver import UserConfigurationSaver
from .UserConfiguration import UserConfiguration

class UserConfigurationManager:
    def __init__(self, name : str):
        self.name = name

    def create(self, filename, proportions={"1":0,"2":0,"3":0,"4":0}): # default parameters for default config for creation
        print(filename)
        if self.name not in self.list_configs(): # if config name not in use
            new_user_config = UserConfiguration(f"{self.name}", proportions) # initialise UserConfiguration dataclass object with data
            UserConfigurationSaver(new_user_config).save(filename) # save config

    def remove(self):
        if self.name in self.list_configs():
            remove(f"./hardware/UserConfigurations/Data/{self.name}.json") # use os.remove() to delete config JSON
            return True
        return False

    @staticmethod
    def get_available_config_name():
        print("lowkey creating")
        configs = UserConfigurationManager.list_configs()
        print(configs)
        i = 1
        while str(i) in configs:
            i += 1
        return i

    @staticmethod
    def list_configs() -> list:
        return [filename.split('.json')[0] for filename in listdir("./hardware/UserConfigurations/Data/")] # list comprehension to contain all confignames

        
    
