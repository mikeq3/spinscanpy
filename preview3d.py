from __future__ import absolute_import
from __future__ import division

import math
#import threading
#import re
#import time
#import os
#import numpy as np

from wx import glcanvas
import wx
try:
	import OpenGL
	OpenGL.ERROR_CHECKING = False
	from OpenGL.GLU import *
	from OpenGL.GL import *
	hasOpenGLlibs = True
except:
	print ("Failed to find PyOpenGL: http://pyopengl.sourceforge.net/")
	hasOpenGLlibs = False

import opengl
import pypoint

class previewPanel(wx.Panel):
	def __init__(self, parent):
		super(previewPanel, self).__init__(parent,-1)
		
		self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))
		self.SetMinSize((640,480))

		self.glCanvas = PreviewGLCanvas(self)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.glCanvas, 1, flag=wx.EXPAND)
		self.SetSizer(sizer)
	
class PreviewGLCanvas(glcanvas.GLCanvas):
	def __init__(self, parent):
		#attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24, glcanvas.WX_GL_STENCIL_SIZE, 8)
		attribList = (glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 24)
		glcanvas.GLCanvas.__init__(self, parent, attribList = attribList)
		self.parent = parent
		self.context = glcanvas.GLContext(self)
		self.p = pypoint.PyPoint(self)
		wx.EVT_PAINT(self, self.OnPaint)
		wx.EVT_SIZE(self, self.OnSize)
		wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
		self._init = False
		self._vlinit = False
		self.viewport = None
		self.state = False
		self.rate = 0.5
		self.rotY = 0
	
	def OnEraseBackground(self,event):
		#Workaround for windows background redraw flicker.
		pass
	
	def OnSize(self,e):
		self.Refresh()

	def __OnInit(self):
		self.SetCurrent(self.context)
		opengl.InitGL(self)
		self._init = True

	def resetView(self):
		if (self._vlinit):
			opengl.InitGL(self)
			self._vlinit = False

	def setCamView(self):
		if not self._vlinit:
			opengl.InitVLGL(self)
			self._vlinit = True

	def OnPaint(self,e):
		dc = wx.PaintDC(self)
		if not hasOpenGLlibs:
			dc.Clear()
			dc.DrawText("No PyOpenGL installation found.\nNo preview window available.", 10, 10)
			return
		if not self._init and not self._vlinit:
			self.__OnInit()
		self.SetCurrent(self.context)
    		#glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		if not self._vlinit:
			glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
			self.p.draw(1.0)
		self.SwapBuffers()
	
	def drawModel(self, state):
		self.state = state
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glLoadIdentity()
		glTranslate(0.0, 200.0, -500.0)
		if (not state and self.rate > 0):
			glRotatef(self.rotY, 0.0, 1.0, 0,0)
			self.rotY += self.rate
		#elif (state):
		#	glRotatef(self.rotY, 0.0, 1.0, 0,0)	
		self.p.draw(1.0)
		self.SwapBuffers()

	def drawVid(self, buff, sizeW, sizeH, format, depth):
		self.setCamView()
		glDrawPixels(sizeW, sizeH, format, depth, buff)
		glBegin(GL_LINES)
		glColor3f(1.0, 1.0, 1.0)
		glVertex2f(0.0, 240.0)
		glVertex2f(640.0, 240.0)
		glVertex2f(320.0, 0.0)
		glVertex2f(320.0, 480.0)
		glEnd()
		self.SwapBuffers()

	def setRotRate(self, rate):
		self.rate = rate
	
	def rotOneLine(self, rotAngle):
		self.rotY += rotAngle


