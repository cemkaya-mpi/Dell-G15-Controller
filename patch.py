def g15_5530_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed"]

def g15_5520_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed"]

def g15_5515_patch(wind):
    del wind.power_modes_dict["USTT_Balanced"]
    del wind.power_modes_dict["USTT_Performance"]
    del wind.power_modes_dict["USTT_Quiet"]
    del wind.power_modes_dict["USTT_FullSpeed"]
    del wind.power_modes_dict["USTT_BatterySaver"]

def g15_5511_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed"]
    del wind.power_modes_dict["USTT_BatterySaver"]
    wind.power_modes_dict["USTT_Cool"] = "0xa2"