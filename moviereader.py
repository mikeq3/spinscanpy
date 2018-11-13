from __future__ import absolute_import

import wx
import cv

class ReadMovie:
	def __init__(self, moviefile):
		self.frameImg = None
		self.vidFile = cv.CaptureFromFile(moviefile)
		self.nFrames = int(  cv.GetCaptureProperty( self.vidFile, cv.CV_CAP_PROP_FRAME_COUNT ) )
		self.fps = cv.GetCaptureProperty( self.vidFile, cv.CV_CAP_PROP_FPS )

	def getFrame(self):
		self.frameImg = cv.QueryFrame(self.vidFile)
		if not (self.frameImg == False):
			cv.CvtColor(self.frameImg, self.frameImg, cv.CV_BGR2RGB)
			self.Img = wx.EmptyImage(self.frameImg.width, self.frameImg.height)
			self.Img.SetData(self.frameImg.tostring())
			return True
		else:
			self.vidFile = None
			return False

	def getBitmap(self):
		if not (self.frameImg == False):
			return wx.BitmapFromImage(self.Img)
		else:
			self.vidFile = None
			return False

	def getScaledBitmap(self, factor):
		if not (self.frameImg == False):
			self.ImgScaled = self.Img.Scale((factor * self.frameImg.width), (factor * self.frameImg.height), wx.IMAGE_QUALITY_HIGH)
			return wx.BitmapFromImage(self.ImgScaled)
		else:
			self.vidFile = None
			return False

	def getScaledImg(self, factor):
		if not (self.frameImg == False):
			self.ImgScaled = self.Img.Scale((factor * self.frameImg.width), (factor * self.frameImg.height), wx.IMAGE_QUALITY_HIGH)
			return self.ImgScaled
		else:
			self.vidFile = None
			return False

	def getImg(self):
		if not (self.frameImg == False):
			return self.Img
		else:
			self.vidFile = None
			return False

	def getCurrentFrame(self):
		self.curFrame = int(  cv.GetCaptureProperty( self.vidFile, cv.CV_CAP_PROP_POS_FRAMES ) )
		return self.curFrame

	def done(self):
		if (self.vidFile == None):
			return True

		self.nextFrame = int(  cv.GetCaptureProperty( self.vidFile, cv.CV_CAP_PROP_POS_FRAMES ) )
		if (self.nextFrame + 1 > self.nFrames):
#		if (self.nextFrame + 1 > 10):  # for testing ##########
			return True
		else:
			return False

	def getFps(self):
		return self.fps

	def getNframes(self):
		return self.nFrames

	def nextFrame(self):
		self.nextFrame = int(  cv.GetCaptureProperty( self.vidFile, cv.CV_CAP_PROP_POS_FRAMES ) )
		self.nextFrame += 1
		return self.nextFrame

