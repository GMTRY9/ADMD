from dataclasses import dataclass

@dataclass
class SystemConfiguration:
    """Class for system configuration"""
    cartridges : int
    flow_rate_l_s : float
    start_button_gpio : int
    stop_button_gpio : int
    next_button_gpio : int
    prev_button_gpio : int
    pump1_gpio : int
    pump2_gpio : int
    pump3_gpio : int
    pump4_gpio : int

    def get_as_dict(self) -> dict:
        return {"cartridges":self.cartridges} | \
            {"flow_rate_l_s":self.flow_rate_l_s} | \
            {"start_button_gpio":self.start_button_gpio} | \
            {"stop_button_gpio":self.stop_button_gpio} | \
            {"next_button_gpio":self.next_button_gpio} | \
            {"prev_button_gpio":self.prev_button_gpio} | \
            {"pump1_gpio":self.pump1_gpio} | \
            {"pump2_gpio":self.pump2_gpio} | \
            {"pump3_gpio":self.pump3_gpio} | \
            {"pump4_gpio":self.pump4_gpio}

# join all config data into large dictionary
    
    def get_cartridges(self) -> int:
        return self.cartridges
    
    def get_flow_rate(self) -> float: # get keybind from button number
        return self.flow_rate_l_s