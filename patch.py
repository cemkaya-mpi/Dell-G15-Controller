def g15_5520_patch(wind):
    del wind.power_modes_dict["USTT_FullSpeed" ]


def g15_5511_patch(wind):
    wind.power_modes_dict.update({"USTT_Balanced" : "0x97",
                                  "USTT_Performance" : "0x98",
                                  "USTT_Quiet" : "0x96",
                                  "USTT_FullSpeed" : "0x99"
                                      })
    del wind.power_modes_dict["USTT_FullSpeed" ]
    del wind.power_modes_dict["USTT_BatterySaver" ]