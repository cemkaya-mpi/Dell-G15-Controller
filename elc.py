#!/usr/bin/python3

import usb
import sys
import struct
from elc_constants import *
from hidreport import *
import binascii

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Action:
	def __init__(self,effect,duration,tempo,red,green,blue):
		self.effect = effect
		self.duration = duration
		self.tempo = tempo
		self.red = red
		self.green = green
		self.blue = blue

	def __str__(self):
		fragment=format(self.effect,'02x')
		fragment+=format(self.duration,'04x')
		fragment+=format(self.tempo,'04x')
		fragment+=format(self.red,'02x')
		fragment+=format(self.green,'02x')
		fragment+=format(self.blue,'02x')
		return fragment

class Elc:

	def build_command(self,fragment) :
		bytes=bytearray.fromhex(fragment)
		bytes+=bytearray.fromhex('00' * (33-len(bytes)))
		return bytes

	def run_command(self,device,fragment) :
		bytes=self.build_command('03' + fragment)
		hid_set_output_report(device,bytes)
		return bytearray(hid_get_input_report(device,33))

	def get_version(self) :
		reply=self.run_command(self.device,format(ELC_QUERY,'02x') + format(GET_VERSION,'02x'))
		return (reply[3],reply[4],reply[5])

	def get_status(self) :
		return 0

	def get_platform(self) :
		reply=self.run_command(self.device,format(ELC_QUERY,'02x') + format(GET_PLATFORM,'02x'))
		return (reply[3:5],reply[5])

	def get_animation_count(self) :
		reply=self.run_command(self.device,format(ELC_QUERY,'02x') + format(GET_ANIMATION_COUNT,'02x'))
		return (struct.unpack('>H',reply[3:5])[0],struct.unpack('>H',reply[5:7])[0])

	def start_new_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(START_NEW,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def finish_save_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(FINISH_SAVE,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def finish_play_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(FINISH_PLAY,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply
		

	def remove_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(REMOVE,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def play_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(PLAY,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def set_default_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(SET_DEFAULT,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def set_startup_animation(self,animation, duration=0) :
		if (animation < 0x5b or animation > 0x60):
			command=USER_ANIMATION
		else:
			command=POWER_ANIMATION
		command=format(command,'02x')
		reply=self.run_command(self.device,command+format(SET_DEFAULT,'04x')+format(animation,"04x"))
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def start_series(self,zones, loop=1) :
		zonestring="".join(format(x,"02x") for x in zones)
		reply=self.run_command(self.device,format(START_SERIES,'02x')+format(loop,"02x")+format(len(zones),"04x")+zonestring)
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def add_action(self,actions) :
		fragment=format(ADD_ACTION,'02x')
		if len(actions) > 3 :
			raise Exception("Too many actions in a single start action")
		for k in actions:
			fragment += str(k)
		reply=self.run_command(self.device,fragment)
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def set_event(self):
		raise Exception("Not implemented on device")

	def dim(self,zones,dimming):
		zonestring="".join(format(x,'02x') for x in zones)
		fragment=format(DIMMING,'02x')+format(dimming,'02x')+format(len(zones),'04x')+zonestring
		reply=self.run_command(self.device,fragment)
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def set_color(self,zones,red,green,blue):
		zonestring="".join(format(x,'02x') for x in zones)
		fragment=format(SET_COLOR,'02x')+format(red,'02x')+format(green,'02x')+format(blue,'02x')+format(len(zones),'04x')+zonestring
		reply=self.run_command(self.device,fragment)
		if (self.debug==1): eprint(binascii.hexlify(reply))
		return reply

	def reset(self):
		raise Exception("Not implemented in this code at this time")

	def spi_flash(self):
		raise Exception("Not implemented in this code at this time")

	def __init__(self,vid,pid,debug=0):
		self.device=usb.core.find(idVendor=vid, idProduct=pid)
		self.debug=debug
		

def main():
	import sys
	vid=int(sys.argv[1],16)
	pid=int(sys.argv[2],16)
	elc=Elc(vid,pid)
	(major,minor,revision) = elc.query_version()
	print("Firmware: %d.%d.%d" % (major,minor,revision))
	return 0

if __name__ == "__main__":
	main()
