from dataclasses import dataclass

@dataclass
class SystemConfiguration:
    """Class for system configuration"""
    cartridges : int
    start_button_gpio : int
    stop_button_gpio : int
    next_button_gpio : int
    prev_button_gpio : int
    pump1_gpio : int
    pump1_flow_rate_l_s : float
    pump2_gpio : int
    pump2_flow_rate_l_s : float
    pump3_gpio : int
    pump3_flow_rate_l_s : float
    pump4_gpio : int
    pump4_flow_rate_l_s : float 

    def get_as_dict(self) -> dict:
        return {"cartridges":self.cartridges} | \
            {"start_button_gpio":self.start_button_gpio} | \
            {"stop_button_gpio":self.stop_button_gpio} | \
            {"next_button_gpio":self.next_button_gpio} | \
            {"prev_button_gpio":self.prev_button_gpio} | \
            {"pump1_gpio":self.pump1_gpio} | \
            {"pump1_flow_rate_l_s":self.pump1_flow_rate_l_s} | \
            {"pump2_gpio":self.pump2_gpio} | \
            {"pump2_flow_rate_l_s":self.pump2_flow_rate_l_s} | \
            {"pump3_gpio":self.pump3_gpio} | \
            {"pump3_flow_rate_l_s":self.pump3_flow_rate_l_s} | \
            {"pump4_gpio":self.pump4_gpio} | \
            {"pump4_flow_rate_l_s":self.pump4_flow_rate_l_s}

# join all config data into large dictionary
    
    def get_cartridges(self) -> int:
        return self.cartridges
    
    def get_flow_rate(self) -> float: # get keybind from button number
        return self.flow_rate_l_s