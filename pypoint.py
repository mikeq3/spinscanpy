from OpenGL.GL import *
import wx
from preview3d import PreviewGLCanvas
import math
import numpy as np
from ctypes import sizeof, c_float, c_void_p, c_uint

class PyPoint(PreviewGLCanvas):
	def __init__(self, parent, *args, **kwargs):
  		self.parent = parent
		self.vbuffer = None
		self.pointdata = None
		self.numPoints = 0
		self.updated = False
		self._binit = False
		self.buffoffset = 0
		float_size = sizeof(c_float)
		self.vertex_offset = c_void_p(0 * float_size)
		self.color_offset = c_void_p(3 * float_size)
		self.record_len = 7 * float_size
		self.buffSize = 400000



	def _initBuf(self):
		self.vbuffer = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbuffer)
		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_COLOR_ARRAY)
		glVertexPointer(3,GL_FLOAT, self.record_len,self.vertex_offset)
		glColorPointer(4,GL_FLOAT,self.record_len,self.color_offset)
		self._binit = True

	def addPoint(self, x, y, z, r, g, b, a):
		self.updated = True
		self.pointdata = np.array([[ x, y, z, r, g, b, a]], dtype=np.float32)
		self.numPoints += 1
		if not (self._binit):
			self._initBuf()
			glBufferData(GL_ARRAY_BUFFER, (self.buffSize*self.record_len), None, GL_STREAM_DRAW)
			glBufferSubData(GL_ARRAY_BUFFER, self.buffoffset, (len(self.pointdata)*self.record_len), self.pointdata)
			self.buffoffset = (len(self.pointdata)*self.record_len)
		else:
			glBufferSubData(GL_ARRAY_BUFFER, self.buffoffset, (len(self.pointdata)*self.record_len), self.pointdata)
			self.buffoffset += (len(self.pointdata)*self.record_len)

	def draw(self, size):			
		if (self.vbuffer != None):
			glPointSize(size)
			glDrawArrays(GL_POINTS,0,self.numPoints)
			self.updated = False

	def clear(self):
			glBindBuffer(GL_ARRAY_BUFFER, 0)
			glDisableClientState(GL_COLOR_ARRAY)
			glDisableClientState(GL_VERTEX_ARRAY)
			self._binit = False

	def setBuffSize(self, size):
			# Size is video height by frame count (480 * 591)
			self.buffSize = size


