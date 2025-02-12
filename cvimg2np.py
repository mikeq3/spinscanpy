from __future__ import absolute_import

import cv2 as cv
from OpenGL.GL import *
import numpy as np

class cv2array:
	def __init__(self):
		self.img = None
		self.depth2dtype = { 
			cv.CV_8U: 'uint8', 
			cv.CV_8S: 'int8', 
			cv.CV_16U: 'uint16', 
			cv.CV_16S: 'int16', 
			cv.CV_32S: 'int32', 
			cv.CV_32F: 'float32', 
			cv.CV_64F: 'float64', 
		} 

		self.depth2GLb = {
			cv.CV_8U: GL_UNSIGNED_BYTE, 
			cv.CV_8S: GL_BYTE, 
			cv.CV_16U: GL_UNSIGNED_SHORT, 
			cv.CV_16S: GL_SHORT, 
			cv.CV_32S: GL_INT, 
			cv.CV_32F: GL_FLOAT, 
			cv.CV_64F: False, 
		} 

		self.nch2format = {
			1: GL_LUMINANCE,
			3: GL_BGR,
			4: GL_BGRA,
		}

	def getdepth(self):
		if (self.img != None):
			dsize = self.depth2GLb[self.img.depth]
			#print dsize
		else:
			dsize = False
		return dsize

	def getformat(self):
		if (self.img != None):
			format = self.nch2format[self.img.nChannels]
		else:
			format = False
		return format

	def getarray(self, img):
		self.img = img
		a = np.fromstring( 
		self.img.tostring(), 
 		dtype=self.depth2dtype[self.img.depth], 
		count=self.img.width*self.img.height*self.img.nChannels) 
		a.shape = (self.img.height,self.img.width,self.img.nChannels) 
		return a

