import json

#from hardware.UserConfigurations import UserConfigurationManager

from .UserConfiguration import UserConfiguration

class UserConfigurationSaver:
    def __init__(self, user_config : UserConfiguration):
        self.userConfig = user_config

    # def get_available_config_name(self):
    #     config_names = UserConfigurationManager.list_configs()
    #     for i in range(1, len(config_names) + 1):
    #         if str(i) != config_names[i].split(".")[0]:
    #             return str(i)

    def save(self, name):
        with open(f"./hardware/UserConfigurations/Data/{name}.json", "w") as out:
            json.dump((
                {"name":self.userConfig.name} | 
                {"proportions":self.userConfig.proportions} |
                {"default_size":self.userConfig.default_size}
                ), out, indent=4) # dump json with data from UserConfiguration object using join to combine dictionaries, indent for aesthetics.
        return
    
