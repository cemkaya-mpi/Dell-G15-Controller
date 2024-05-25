def g15_5520_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed" ]
    
def g15_5511_patch(wind):
    wind.power_modes_dict = {
        "Quiet" : "0x96",
        "Balanced" : "0x97",
        "Performance" : "0x98",
        "FullSpeed" : "0x99",
        "G Mode" : "0xab",
        "Manual" : "0x0",
    }