from __future__ import absolute_import

import serial

class SerialCfg:
	def __init__(self):
		self.baud = { 
			'115200': 115200, 
			'57600': 57600, 
			'38400': 38400, 
			'19200': 19200, 
			'9600': 9600,  
		}
		self.bytes = { 
			'Eight': serial.EIGHTBITS, 
			'Seven': serial.SEVENBITS,  
		}
		self.parity = { 
			'None': serial.PARITY_NONE, 
			'Even': serial.PARITY_EVEN, 
			'Odd': serial.PARITY_ODD,  
		}
		self.stop = { 
			'One': serial.STOPBITS_ONE, 
			'Two': serial.STOPBITS_TWO, 
		}

		self.serialsettings = [ 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE]
		self.serialcfg = ['9600','Eight','None','One']

	def setBaud(self, bd):
		self.serialsettings[0] = self.baud[bd]
		self.serialcfg[0] = bd
		return True
	
	def setBytes(self, bit):
		self.serialsettings[1] = self.bytes[bit]
		self.serialcfg[1] = bit
		return True

	def setParity(self, pty):
		self.serialsettings[2] = self.parity[pty]
		self.serialcfg[2] = pty
		return True

	def setStop(self, stp):
		self.serialsettings[3] = self.stop[stp]
		self.serialcfg[3] = stp
		return True

	def getcfg(self):
		return self.serialsettings
		
	def getvalues(self):
		return self.serialcfg

