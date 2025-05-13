from dataclasses import dataclass

@dataclass
class SystemConfiguration:
    """Class for system configuration"""
    cartridges : int
    flow_rate_l_s : float

    def get_as_dict(self) -> dict:
        return {"cartridges":self.cartridges} | {"flow_rate_l_s":self.flow_rate_l_s} # join all config data into large dictionary
    
    def get_cartridges(self) -> int:
        return self.cartridges
    
    def get_flow_rate(self) -> float: # get keybind from button number
        return self.flow_rate_l_s
    
    def set_cartridges(self, cartridges : int):
        self.cartridges = cartridges
    
    def set_flow_rate(self, flow_rate : float):
        self.flow_rate_l_s = flow_rate