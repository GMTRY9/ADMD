from .UserConfigurations import *
from .SystemConfigurations import *

class DrinkMachine():
    def __init__(self, otp : str):
        self.NUM_CARTRIDGES = SystemConfigurationLoader().load().get_cartridges()
        
        self.otp = otp
        self.configs = UserConfigurationManager.list_configs()
        self.last_config_no = len(self.configs)
        self.selected_config = 0

    def increment_config_selection(self):
        self.selected_config += 1
        if self.selected_config > self.last_config_no - 1:
            self.selected_config = 1
        return self.selected_config
    
    def set_selected_config_index(self, config_id):
        self.selected_config = config_id

    def set_selected_config_name(self, config_name):
        self.selected_config = self.configs.index(config_name)
    
    def get_selected_size(self):
        # get size entered by user
        return
    
    def get_selected_config_index(self):
        return self.selected_config
    
    def get_selected_config_name(self):
        return self.configs[self.selected_config]
    
    def update_display(self, text : str):
        return True
    
    def start(self):
        config = UserConfigurationLoader(str(self.selected_config)).load()
        proportions = config.get_all_proportions()
        # size = self.get_selected_size()
        size = int(config.get_default_size())

        final_proportion_values = {}
        denominator = sum(int(v) for v in proportions.values())

        for key, value in proportions.items():
            final_proportion_values[key] = size * int(value) / denominator

        print(final_proportion_values)


    