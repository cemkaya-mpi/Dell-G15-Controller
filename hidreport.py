import usb
def hid_set_output_report(dev, report, report_id=0):
      """ Implements HID SetReport via USB control transfer """
      dev.ctrl_transfer(
          0x21, # REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_OUT
          9, # SET_REPORT
          0x200+report_id, 0x00,
          report)

def hid_get_input_report(dev,length,report_id=0):
      """ Implements HID GetReport via USB control transfer """
      return dev.ctrl_transfer(
          0xA1, # REQUEST_TYPE_CLASS | RECIPIENT_INTERFACE | ENDPOINT_IN
          1, # GET_REPORT
          0x100+report_id, 0x00,
          length)

