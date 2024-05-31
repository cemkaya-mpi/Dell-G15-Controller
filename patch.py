def g15_5520_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed" ]
    
def g15_5511_patch(wind):
    wind.power_modes_dict = {
        "Balanced" : "0xa0",
        "Performance" : "0xa1",
        "Cool" : "0xa2",
        "Quiet" : "0xa3",
       #"USTT_FullSpeed" : "0xa4", # Hidden for 5511
       #"USTT_BatterySaver" : "0xa5", Hidden for 5511
        "G Mode" : "0xab",
        "Manual" : "0x0",
    }
