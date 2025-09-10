from dataclasses import dataclass

@dataclass
class UserConfiguration:
    """Class for user configurations"""
    name : str
    proportions : dict

    def get_as_dict(self) -> dict:
        return {"name":self.name} | {"proportions":self.proportions} # join all config data into large dictionary
    
    def get_name(self) -> str:
        return str(self.name)
    
    def get_num_used_cartridges(self) -> int:
        return len(self.proportions)

    def get_proportion(self, cartridgeNo : str) -> int: # get keybind from button number
        return self.proportions[cartridgeNo] 

    def get_all_proportions(self) -> dict: # get all button number and keybind associations
        return dict(self.proportions)
    
    def set_proportion(self, cartridgeNo : str, ratio : float): # create or overwrite keybind association to button number 
        self.proportions[cartridgeNo] = ratio
        return
    
    def set_name(self, name : str):
        self.name = name