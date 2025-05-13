import json

from .SystemConfiguration import SystemConfiguration

class SystemConfigurationSaver:
    def __init__(self, user_config : SystemConfiguration):
        self.userConfig = user_config

    def save(self):
        with open(f"./hardware/SystemConfigurations/system_config.json", "w") as out:
            json.dump((
                {"cartridges":self.userConfig.cartridges} | 
                {"flow_rate_l_s":self.userConfig.flow_rate_l_s}
                ), out, indent=4) # dump json with data from UserConfiguration object using join to combine dictionaries, indent for aesthetics.
        return
    
