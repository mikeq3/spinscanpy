from __future__ import absolute_import

import sys

class createWriter:
	def __init__(self, filename):
		self.mode = "r"
		self.filename = filename
		
	def openf(self):
		self.fd = open(self.filename, self.mode)
		return True

	def getfd(self):
		return 	self.fd

	def setMode(self, mode):
		self.mode_set = set(['r+','r','w','a'])
		if (mode in self.mode_set):
			self.mode = mode
			return True
		else:
			return False

	def close(self):
		return self.fd.close()
	
	def read(self):
		return self.fd.read()

	def readline(self):
		return self.fd.readline()

	def write(self, text):
		return self.fd.write(text)

