def g15_5520_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed" ]


def g15_5511_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed" ]
    del wind.power_modes_dict["USTT_BatterySaver" ]