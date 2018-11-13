from __future__ import absolute_import

import wx
import cv
#from wx import glcanvas
from OpenGL.GL import *
import serial
import threading
import sys
import pygst
import os
import platform
import shutil
import glob
import warnings
import re
import math
from time import sleep
import pypoint
import opengl
import preview3d
from moviereader import ReadMovie
from filewriter import createWriter
from serialcfg import SerialCfg
from cvimg2np import cv2array
from cfgwindow import NewWindow
#import random
from preview3d import PreviewGLCanvas
import numpy as np
from cv import *
from optparse import OptionParser
import json
#Only import the _core to save import time
import wx._core

version = "1.00"
outputFolder = "Output/"
scanFolder = "Scans/"
laserFile = "laser.avi"
textureFile = "texture.avi"
plyFilename = "scan.ply"
pcloudFilename = "pcloud.json"
radiansToDegrees = 180.0 / 3.14159
degreesToRadians = 3.14159 / 180.0
# degrees 56 zoom in 75 zoom out
camVFOV = 75.0
# degrees
camHFOV = (camVFOV * 3.75) / 5.0
# from camera to center of table in mm
camDistance = 304.8 # 1 foot = 304.8
# degrees
laserOffset = 30.0 # 15? 45?

def main():
	#parser = OptionParser(usage="usage: %prog [options] <filename>.stl")
	#parser.add_option("-i", "--ini", action="store", type="string", dest="profileini",
	#	help="Load settings from a profile ini file")
	#parser.add_option("-r", "--print", action="store", type="string", dest="printfile",
	#	help="Open the printing interface, instead of the normal cura interface.")
	#parser.add_option("-p", "--profile", action="store", type="string", dest="profile",
	#	help="Internal option, do not use!")
	#parser.add_option("-s", "--slice", action="store_true", dest="slice",
	#	help="Slice the given files instead of opening them in Cura")
	#(options, args) = parser.parse_args()
	ScanApp().MainLoop()

class ScanApp(wx.App):
	def __init__(self):
		if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
			super(ScanApp, self).__init__(redirect = True, filename = 'output.txt')
		else:
			super(ScanApp, self).__init__(redirect = False)

		self.mainWindow = mainWindow()

class ctrlPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
  		self.parent = parent
		
		self.Recording = False

		#self.SetBackgroundColour('#000000')

		comList = self.parent.serialList()
		ttycombo = wx.ComboBox(self, wx.ID_ANY, 'Serial Port', wx.DefaultPosition,
                            (200,-1), comList, wx.CB_DROPDOWN)
		ttycombo.SetToolTip(wx.ToolTip("select serial port of arduino from dropdown-list"))
		camList = self.parent.camList()
        	camcombo = wx.ComboBox(self, wx.ID_ANY, 'Camera', wx.DefaultPosition,
                            (200,-1), camList, wx.CB_DROPDOWN)
		camcombo.SetToolTip(wx.ToolTip("select camera device from dropdown-list"))
		self.cbll = wx.CheckBox(self, -1, 'Laser Left')
		self.cblr = wx.CheckBox(self, -1, 'Laser Right')
		self.textureButton = wx.Button(self, -1, 'Record &Texture')
		self.lslButton = wx.Button(self, -1, 'Record &Left Laser')
		self.lsrButton = wx.Button(self, -1, 'Record &Right Laser')
		self.tsButton = wx.Button(self, -1, 'Test &Spin')
		self.otsButton = wx.Button(self, -1, 'Open &Texture Scan')
		self.olsButton = wx.Button(self, -1, 'Open &Laser Scan')
		self.absButton = wx.Button(self, -1, 'A&bort Scan')
		self.procButton = wx.Button(self, -1, '&Process Scans')
		self.procButton.SetToolTipString("This is to analyze a scan file!")
		self.cbpcapp = wx.CheckBox(self, -1, '&Combine with Previous Cloud')
         	self.rbl = wx.RadioButton(self, -1, 'Left Scan', style=wx.RB_GROUP)
		self.rbr = wx.RadioButton(self, -1, 'Right Scan')
		self.stpprocButton = wx.Button(self, -1, '&Abort Processing')
		self.progText = wx.StaticText(self, -1, 'Progress:')
		self.progText2 = wx.StaticText(self, -1, '')
		self.progressBar = wx.Gauge(self, -1, range=100, size=(228,25), name="Progress")

		#self.Bind(wx.EVT_BUTTON, lambda e: self.parent._showModelLoadDialog(1), self.loadButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnTextureScan, self.textureButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnRightLaserScan, self.lsrButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnLeftLaserScan, self.lslButton)
		self.Bind(wx.EVT_BUTTON, self.parent.testSpin, self.tsButton)
		self.Bind(wx.EVT_BUTTON, self.parent.openTextureScan, self.otsButton)
		self.Bind(wx.EVT_BUTTON, self.parent.openLaserScan, self.olsButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnStopScan, self.absButton)
		self.Bind(wx.EVT_CHECKBOX, self.parent.OnAppendPC, self.cbpcapp)
		self.Bind(wx.EVT_RADIOBUTTON, self.parent.GetScanSide, self.rbl)
		self.Bind(wx.EVT_RADIOBUTTON, self.parent.GetScanSide, self.rbr)
		self.Bind(wx.EVT_BUTTON, self.parent.OnProcess, self.procButton)
		self.Bind(wx.EVT_BUTTON, self.parent.OnStopProcess, self.stpprocButton)
		self.Bind(wx.EVT_COMBOBOX, self.parent.OnCamSelect, camcombo)
		self.Bind(wx.EVT_COMBOBOX, self.parent.OnComSelect, ttycombo)
		self.Bind(wx.EVT_CHECKBOX, self.parent.OnLaserRight, self.cblr)
		self.Bind(wx.EVT_CHECKBOX, self.parent.OnLaserLeft, self.cbll)

		self.sizer = wx.GridBagSizer()
		self.sizer.Add(ttycombo, pos=(0,0),  span=(1, 2),flag=wx.ALL, border=5)
        	self.sizer.Add(camcombo, pos=(1,0),  span=(1, 2),flag=wx.ALL, border=5)
		self.sizer.Add(self.cbll, pos=(2,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.cblr, pos=(2,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.textureButton, pos=(3,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.lsrButton, pos=(3,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.lslButton, pos=(4,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.tsButton, pos=(4,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.absButton, pos=(5,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.cbpcapp, pos=(20,0), span=(1, 2),flag=wx.ALL, border=5)
		self.sizer.Add(self.rbl, pos=(21,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.rbr, pos=(21,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.procButton, pos=(22,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.stpprocButton, pos=(22,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.otsButton, pos=(24,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.olsButton, pos=(24,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.progText, pos=(25,0), flag=wx.ALL, border=5)
		self.sizer.Add(self.progText2, pos=(25,1), flag=wx.ALL, border=5)
		self.sizer.Add(self.progressBar, pos=(26,0), span=(1, 2), flag=wx.ALL, border=5)
		self.SetSizer(self.sizer)
		#self.sizer.Fit(self)
		self.Layout()

	def disableProcBtn(self):
		self.procButton.Enable(False)

	def enableProcBtn(self):
		self.procButton.Enable(True)
		
class mainWindow(wx.Frame):
	TIMER_PLAY_ID = 101
	TIMER_SERIAL_ID = 102
	def __init__(self):
		super(mainWindow, self).__init__(None, title='SpinscanPy - ' + version, pos=(200, 150), size=(911, 781))

		wx.EVT_CLOSE(self, self.OnClose)

		#self.SetBackgroundColour('#000000')

        	self.playTimer = wx.Timer(self, self.TIMER_PLAY_ID)
        	wx.EVT_TIMER(self, self.TIMER_PLAY_ID, self.onTimer)

		self.playTimer.Start(1000/15) #assuming 15 fps

      		self.Bind(wx.EVT_PAINT, self.onPaint)

		self.normalModeOnlyItems = []
		self.menubar = wx.MenuBar()
		self.fileMenu = wx.Menu()
		#i = self.fileMenu.Append(wx.ID_SAVE, '&Save')
		#self.Bind(wx.EVT_MENU, self.OnSave, i)
		i = self.fileMenu.Append(wx.ID_EXIT, 'Quit')
		self.Bind(wx.EVT_MENU, self.OnQuit, i)
		self.menubar.Append(self.fileMenu, '&File')
		self.toolsMenu = wx.Menu()
		i = self.toolsMenu.Append(wx.ID_PROPERTIES, '&Settings')
		self.Bind(wx.EVT_MENU, self.OnSettings, i)
		#i = self.toolsMenu.Append(wx.ID_CLOSE_ALL, '&Abort Scan')
		self.menubar.Append(self.toolsMenu, '&Tools')
		#self.Bind(wx.EVT_MENU, self.OnStopScan, i)
		helpMenu = wx.Menu()
		i = helpMenu.Append(wx.ID_ABOUT, "&About")
		self.Bind(wx.EVT_MENU, self.OnAbout, i)
		self.menubar.Append(helpMenu, '&Help')
		self.SetMenuBar(self.menubar)

		self.preview3d = preview3d.previewPanel(self)

		self.laserpanel = wx.Panel(self,-1, size=(320,240))
		self.texturepanel = wx.Panel(self,-1, size=(320,240))

		self.texturepanel.SetBackgroundColour('#00c000')
		self.laserpanel.SetBackgroundColour('#b00000')
		self.ctrpnl = ctrlPanel(self)
		self.sb = self.CreateStatusBar()
		
		self.bagSizer = wx.GridBagSizer(hgap=2, vgap=2)
		
		self.bagSizer.Add(self.preview3d, pos=(0,1), span=(1,2), flag=wx.ALL|wx.SHAPED, border=2)
		self.bagSizer.Add(self.ctrpnl, pos=(0,0), span=(2,1), flag=wx.ALL|wx.EXPAND, border=2)
		self.bagSizer.Add(self.texturepanel, pos=(1,1), flag=wx.ALL|wx.SHAPED, border=2)
		self.bagSizer.Add(self.laserpanel, pos=(1,2), flag=wx.ALL|wx.SHAPED, border=2)
		self.bagSizer.Add(self.sb, pos=(2,0), span=(1,2), flag=wx.ALL, border=2)
		self.SetSizer(self.bagSizer)
		self.fmSize = (640, 480)
		self.Camera = "None"
		self.ttyPort = "None"
		self.CamConnect = False
		self.brightness = 0.0
		self.contrast = 0.125
		self.serialConnected = False
		self.textureScanLoaded = False
		self.textureImage = None
		self.laserImage = None
		self.capImg = None
		self.laserScanLoaded = False
		self.pointList = []
		self.normalList = []
		self.colorList = []
		self.cloudList = []
		self.Recording = False
		self.recordingType = ""
		self.serialResponse = ""
		self.Processing = False
		self.appendCloud = False
		self.inTimer = False
		self.sSide = 1.0
		self.percent = 1
		self.frame = 1
		self.numframes = 0
		self.Preview = True
		self.prevframe = 1
		self.threshold = 30
		self.fileprefix = ''
		self.StopPlay = False
		self.cfgValues = [self.fileprefix,str(camHFOV),str(camVFOV),str(camDistance),str(laserOffset),str(self.threshold)]
		self.Img = ""
		self.frameSkip = 1
       		self.Layout()
		self.Show(True)
		self.ctrpnl.stpprocButton.Show(False)
		self.ctrpnl.absButton.Show(False)
		self.ctrpnl.cbpcapp.Show(False)
		self.ctrpnl.rbl.Show(False)
		self.ctrpnl.rbr.Show(False)
		self.sercfg = SerialCfg()

	def _showOpenDialog(self, title, wildcard = "*.avi"):
		dlg=wx.FileDialog(self, title, "nothing", style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
		dlg.SetWildcard(wildcard)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetPath()
			dlg.Destroy()
			if not(os.path.exists(filename)):
				return False
			return filename
		dlg.Destroy()
		return False

	def _showModelLoadDialog(self, amount):
		filelist = []
		for i in xrange(0, amount):
			filelist.append(self._showOpenDialog("Select file to process"))
			if filelist[-1] == False:
				return False
		laserFile = filelist[0]
		print (filelist[0])

	def OnSettings(self, e):
        	self.new = NewWindow(parent=self, id=-1, scfg=self.sercfg, cfgval=self.cfgValues)
        	self.new.Show()

	def OnSave(self, e):
		saveFileDialog = wx.FileDialog(self, "File to save scan", "", "",
                                   "AVI files (*.avi)|*.avi", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if saveFileDialog.ShowModal() == wx.ID_CANCEL:
			return  False   # the user changed idea..
		laserFile += saveFileDialog.GetPath()
		print laserFile

	def OnAbout(self,e):
           	# A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
           	dlg = wx.MessageDialog( self, "Spinscan in Python\nVersion " + version + "\nWritten by\nMike Queally", "About Spinscan", wx.OK)
          	dlg.ShowModal() # Show it
         	dlg.Destroy() # finally destroy it when finished.

	def InitCam(self):
		if (self.CamConnect == False) and (self.Camera != "None"):
        		self.capture = cv.CaptureFromCAM(int(self.Camera[-1:]))
			cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640)
			cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
			cv.SetCaptureProperty(self.capture, CV_CAP_PROP_BRIGHTNESS, self.brightness)
			cv.SetCaptureProperty(self.capture, CV_CAP_PROP_CONTRAST, self.contrast)
        		self.capImg = cv.QueryFrame(self.capture)
			self.cv2arr = cv2array()
 			self.CamConnect = True
			self.Refresh()

	def InitSerial(self):
		print "serial port open " + self.ttyPort + "\n"
		cfg = self.sercfg.getcfg()
		self.serial = serial.Serial(port=self.ttyPort, baudrate=cfg[0], bytesize=cfg[1], parity=cfg[2], stopbits=cfg[3])
		self.serialConnected = True
		self.comTimer = wx.Timer(self, self.TIMER_SERIAL_ID)
        	wx.EVT_TIMER(self, self.TIMER_SERIAL_ID, self.serialThread)
		self.comTimer.Start(1000/20)
		return

    	def onPaint(self, evt):
		if (self.CamConnect and self.Preview):
        		if (self.capImg != None):
				imgArr = self.cv2arr.getarray(self.capImg)
				idepth = self.cv2arr.getdepth()
				iformat = self.cv2arr.getformat()
				self.preview3d.glCanvas.drawVid(imgArr, self.capImg.width, self.capImg.height, iformat, idepth)

		if (self.textureScanLoaded):
			self.textureDC = wx.AutoBufferedPaintDC(self.texturepanel)
        		self.textureDC.DrawBitmap(self.textureImage, 0, 0)

		if (self.laserScanLoaded):
			self.laserDC = wx.AutoBufferedPaintDC(self.laserpanel)
        		self.laserDC.DrawBitmap(self.laserImage, 0, 0)

    	def onTimer(self, evt):
		if (self.CamConnect and self.Preview and not self.Processing):        	
			self.capImg = cv.QueryFrame(self.capture)
        		if self.capImg:
		   		if self.Recording:
		   			cv.WriteFrame(self.writer, self.capImg)
					return
		   		else:
					imgArr = self.cv2arr.getarray(self.capImg)
					idepth = self.cv2arr.getdepth()
					iformat = self.cv2arr.getformat()
					self.preview3d.glCanvas.drawVid(imgArr, self.capImg.width, self.capImg.height, iformat, idepth)
					wx.Yield()

		elif (self.Processing):
		    if (self.laserScanLoaded):
			if (self.laserMovie.done()):
				print "Writing ply file..\n"
				self.ctrpnl.progText2.SetLabel('Writing ply file')
				self.sb.SetStatusText('Writing ply file..')
				wx.Yield()
				if (len(self.fileprefix) > 0):
					plydata = self.fileprefix + '-' + plyFilename
				else:
					plydata = plyFilename
				plydata = outputFolder + plydata
				self.plyFile = createWriter(plydata)
				self.plyFile.setMode('w')
				self.plyFile.openf()
				self.plyFile.write("ply\n")
				self.plyFile.write("format ascii 1.0\n")
				self.plyFile.write("comment Made with spinscanpy!\n")
				self.plyFile.write("element vertex " + str(len(self.pointList)) + "\n")
				self.plyFile.write("property float x\n")
				self.plyFile.write("property float y\n")
				self.plyFile.write("property float z\n")
				#self.plyFile.write("property float nx\n")
				#self.plyFile.write("property float ny\n")
				#self.plyFile.write("property float nz\n")
				if (self.textureScanLoaded):
					self.plyFile.write("property uchar red\n")
					self.plyFile.write("property uchar green\n")
					self.plyFile.write("property uchar blue\n")
				self.plyFile.write("element face 0\n")
				self.plyFile.write("property list uchar int vertex_indices\n")
				self.plyFile.write("end_header\n")
				# add points here
				for x in xrange (0, len(self.pointList)):
					Point = self.pointList[x]
					#Normal = self.normalList[x]
					if (self.textureScanLoaded):
						ColorPoint = self.colorList[x]
						self.plyFile.write(str(Point[0]) + " " + str(Point[1]) + " " + str(Point[2]) + " " + str(ColorPoint[0]) + " " + str(ColorPoint[1]) + " " + str(ColorPoint[2]) + "\n")
					else:
						self.plyFile.write(str(Point[0]) + " " + str(Point[1]) + " " + str(Point[2]) + "\n")

					#self.plyFile.write(str(Point[0]) + " " + str(Point[1]) + " " + str(Point[2]) + " " + str(Normal[0]) + " " + str(Normal[1]) + " " + str(Normal[2]) + " " + str(ColorPoint[0]) + " " + str(ColorPoint[1]) + " " + str(ColorPoint[2]) + "\n")

				self.plyFile.close()

				print "Writing pcloud file..\n"
				self.sb.SetStatusText('Writing pcloud file..')
				self.ctrpnl.progText2.SetLabel('Writing pcloud file')
				if (len(self.fileprefix) > 0):
					pclouddata = self.fileprefix + '-' + pcloudFilename
				else:
					pclouddata = pcloudFilename
				pclouddata = outputFolder + pclouddata
				self.pcloudFile = createWriter(pclouddata)
				self.pcloudFile.setMode('w')
				self.pcloudFile.openf()
				self.pcloudFile.write("[\n")

				# add points here
				for i in xrange (0, len(self.cloudList)):
        				self.pcloudFile.write("\t[\n")
        				Cloud = self.cloudList[i]
        				for s in xrange (0, len(Cloud)):
          					CloudPoint = Cloud[s]
          					self.pcloudFile.write("\t\t[" + str(CloudPoint[0]) + "," + str(CloudPoint[1]) + "," + str(CloudPoint[2]) + "," + str(CloudPoint[3]) + "," + str(CloudPoint[4]) + "," + str(CloudPoint[5]) + "]")
					 	if (s + 1 == len(Cloud)):
							self.pcloudFile.write("\n")
						else:
							self.pcloudFile.write(",\n")
        
        				self.pcloudFile.write("\t]")
					if (i + 1 == len(self.cloudList)):
						self.pcloudFile.write("\n")
					else:
						self.pcloudFile.write(",\n")

				self.pcloudFile.write("]\n")
				self.pcloudFile.close()
				print "Finished!\n"
				self.sb.SetStatusText('Finished!')
				self.ctrpnl.progText2.SetLabel('')
				self.ctrpnl.stpprocButton.Show(False)
				self.ctrpnl.procButton.Show(True)
				self.ctrpnl.rbl.Show(False)
				self.ctrpnl.rbr.Show(False)
      				self.Processing = False;
			else:
				self.processScanFrame()
				if (self.sSide == 1.0):
					self.preview3d.glCanvas.rotOneLine(-360.0/self.numframes)
				else:
					self.preview3d.glCanvas.rotOneLine(360.0/self.numframes)
				wx.Yield()
				self.frame += self.frameSkip

		if (self.textureScanLoaded):
			self.textureDC = wx.AutoBufferedPaintDC(self.texturepanel)
        		self.textureDC.DrawBitmap(self.textureImage, 0, 0)
			#wx.StaticBitmap(self.texturepanel, -1, self.textureImage, (0,0), (320,240))

		if (self.laserScanLoaded):
			self.laserDC = wx.AutoBufferedPaintDC(self.laserpanel)
        		self.laserDC.DrawBitmap(self.laserImage, 0, 0)
			#wx.StaticBitmap(self.laserpanel, -1, self.laserImage, (0,0), (320,240))

		if not (self.Preview):
			if not (self.Processing):
				self.preview3d.glCanvas.setRotRate(0.5)
			self.preview3d.glCanvas.drawModel(self.Processing)
      		evt.Skip()

	def GetScanSide(self, e):
		if (self.ctrpnl.rbr.GetValue()):
			self.sSide = -1.0
		elif (self.ctrpnl.rbl.GetValue()):
			self.sSide = 1.0

	def OnStopScan(self, evt):
		if self.Recording:
			print "Aborting Scan..\n";
			self.sb.SetStatusText('Aborting Scan..')
			self.Recording = False
			self.recordingType = ""
			self.writer = None
			self.ctrpnl.absButton.Show(False)
			self.ctrpnl.textureButton.Show(True)
			self.ctrpnl.lslButton.Show(True)
			self.ctrpnl.lsrButton.Show(True)
			self.ctrpnl.cbll.Show(True)
			self.ctrpnl.cblr.Show(True)
			self.ctrpnl.tsButton.Show(True)
		return
		
	def OnComSelect(self, e):
		self.ttyPort = e.GetString()
		if self.ttyPort != "None":
 			self.InitSerial()

	def OnProcess(self, e):
		if not self.Processing and self.laserScanLoaded:
			self.sb.SetStatusText('')
    			self.Preview = False;
			self.pointList = []
			self.normalList = []
			self.colorList = []
			self.cloudList = []
			if (self.appendCloud):
				self.ctrpnl.cbpcapp.SetValue(False)
				self.ctrpnl.cbpcapp.Show(False)
				print "Getting previous Point Cloud\n"
				self.sb.SetStatusText('Getting previous Point Cloud')
				wx.Yield()
				ppc = prevPcloud(pcloudFilename)
				psize = ppc.getSize()
				clarray = ppc.getarray()
				self.preview3d.glCanvas.p.setBuffSize((480 * self.numframes) + (480 * psize))
				print "Adding previous Point Cloud\n"
				self.sb.SetStatusText('Adding previous Point Cloud')
				self.fillArray(clarray)
				self.appendCloud = False
			else:
				self.ctrpnl.cbpcapp.Show(False)
				self.preview3d.glCanvas.p.setBuffSize(480 * self.numframes)
			self.sb.SetStatusText('')
			self.preview3d.glCanvas.resetView()
  			self.Processing = True
			self.ctrpnl.stpprocButton.Show(True)
			self.ctrpnl.procButton.Show(False)

	def laserScan(self, Side):
		if not self.Recording and not self.Processing:
		    if (self.serialConnected and self.CamConnect):
			if (len(self.fileprefix) > 0):
				laserdata = self.fileprefix + '-' + laserFile
			else:
				laserdata = laserFile
			laserdata = scanFolder + laserdata
			self.writer = cv.CreateVideoWriter(laserdata, CV_FOURCC('M', 'J', 'P', 'G'), 15, self.fmSize, 1)		
      			if (Side == 0):
				self.ctrpnl.rbr.SetValue(True)
				self.sSide = -1.0
        			self.serial.write('5')
      			else:
				self.ctrpnl.rbl.SetValue(True)
				self.sSide = 1.0
        			self.serial.write('6')

			self.recordingType = "laser"
			self.Recording = True;
			self.ctrpnl.absButton.Show(True)
			self.ctrpnl.textureButton.Show(False)
			self.ctrpnl.lslButton.Show(False)
			self.ctrpnl.lsrButton.Show(False)
			self.ctrpnl.cbll.Show(False)
			self.ctrpnl.cblr.Show(False)
			self.ctrpnl.tsButton.Show(False)
			self.sb.SetStatusText('Recording...')
		    else:
			print "ERROR: Serial port not connected or Camera not connected\n"
			self.sb.SetStatusText('ERROR: Serial port not connected or Camera not connected')
		else:
			print "Already Recording or Currently Processing!!\n"
			self.sb.SetStatusText('Already Recording or Currently Processing!!')


	def OnTextureScan(self, e):
		if not self.Recording and not self.Processing:
		    if (self.serialConnected and self.CamConnect):
			if (len(self.fileprefix) > 0):
				texturedata = self.fileprefix + '-' + textureFile
			else:
				texturedata = textureFile
			texturedata = scanFolder + texturedata
			self.writer = cv.CreateVideoWriter(texturedata, CV_FOURCC('M', 'J', 'P', 'G'), 15, self.fmSize, 1)
        		self.serial.write('4')

			self.recordingType = "texture"
			self.Recording = True;
			self.ctrpnl.absButton.Show(True)
			self.ctrpnl.textureButton.Show(False)
			self.ctrpnl.lslButton.Show(False)
			self.ctrpnl.lsrButton.Show(False)
			self.ctrpnl.cbll.Show(False)
			self.ctrpnl.cblr.Show(False)
			self.ctrpnl.tsButton.Show(False)
			self.sb.SetStatusText('Recording...')
		    else:
			print "ERROR: Serial port not connected or Camera not connected\n"
			self.sb.SetStatusText('ERROR: Serial port not connected or Camera not connected')
		else:
			print "Already Recording or Currently Processing!!\n"
			self.sb.SetStatusText('Already Recording or Currently Processing!!')

	def OnClose(self, e):
		print "Closing..\n"
		self.playTimer.Stop()
		if (self.serialConnected):
			self.comTimer.Stop()
		if (threading.activeCount() > 0):
			sleep(0.3)
		self.Destroy()

	def OnQuit(self, e):
		print "Quitting..\n"
		self.playTimer.Stop()
		if (self.serialConnected):
			self.comTimer.Stop()
		if (threading.activeCount() > 0):
			sleep(0.3)
		self.Close()

	def OnCamSelect(self, e):
		self.Camera = e.GetString()[-1:]
		if self.Camera != "None":
			if not (self.Processing):
				if (self.textureScanLoaded):
					self.textureScanLoaded = False
					self.textureMovie = None
				if (self.laserScanLoaded):
					self.laserScanLoaded = False
					self.laserMovie = None
				self.preview3d.glCanvas.setCamView()
				self.Preview = True
			self.InitCam()		

	def OnLeftLaserScan(self, e):
		self.laserScan(1)

	def OnRightLaserScan(self, e):
		self.laserScan(0)

	def OnLaserRight(self, e):
		if (self.serialConnected):
			if (e.IsChecked()):
				self.Laser(1, True)
			else:
				self.Laser(1, False)
		else:
			self.ctrpnl.cblr.SetValue(False)
			print "ERROR: Serial port not connected\n"
			self.sb.SetStatusText('ERROR: Serial port not connected')

	def OnLaserLeft(self, e):
		if (self.serialConnected):
			if (e.IsChecked()):
				self.Laser(0, True)
			else:
				self.Laser(0, False)
		else:
			self.ctrpnl.cbll.SetValue(False)
			print "ERROR: Serial port not connected\n"
			self.sb.SetStatusText('ERROR: Serial port not connected')

	def Laser(self, Side, Enable):
		if (self.serialConnected) and not (self.Recording):
			print "laser: " + str(Side) + " " + str(Enable) + "\n"
			if (Side == 0):
      				if (Enable):
        				self.serial.write('1')
				else:
					self.serial.write('0')
			else:
				if (Enable):
        				self.serial.write('3')
				else:
					self.serial.write('2')
		else:
			if (Side == 0):
				self.ctrpnl.cbll.SetValue(False)
			else:
				self.ctrpnl.cblr.SetValue(False)
			print "ERROR: Currently Recording\n"
			self.sb.SetStatusText('ERROR: Currently Recording')

	def openTextureScan(self, e):
		self.loadTextureScan()

	def openLaserScan(self, e):
		self.loadLaserScan()

	def loadTextureScan(self):
		if (not self.textureScanLoaded and self.laserScanLoaded):
			self.textureMovie = None
			if (len(self.fileprefix) > 0):
				texturedata = self.fileprefix + '-' + textureFile
			else:
				texturedata = textureFile
			texturedata = scanFolder + texturedata
			if not(os.path.exists(texturedata)):
				self.sb.SetStatusText(texturedata + ' File not found select a filename to open')
				texturedata = self._showOpenDialog("Select texture file to process", wildcard = "*texture.avi")
				if not texturedata:
					return
			self.textureMovie = ReadMovie(texturedata)
			self.textureMovie.getFrame()
			self.textureImage = self.textureMovie.getScaledBitmap(0.5)
			self.textureScanLoaded = True

			print 'Num. Frames = ', self.textureMovie.getNframes()
			print 'Frame Rate = ', self.textureMovie.getFps(), ' frames per sec'
			self.sb.SetStatusText('Num. Frames = ' + str(self.textureMovie.getNframes()) + ' + ' + 'Frame Rate = ' + str(self.textureMovie.getFps()) + ' frames per sec')

	def loadLaserScan(self):
		if not (self.laserScanLoaded):
			self.laserMovie = None
			if (len(self.fileprefix) > 0):
				laserdata = self.fileprefix + '-' + laserFile
			else:
				laserdata = laserFile
			laserdata = scanFolder + laserdata
			if not(os.path.exists(laserdata)):
				self.sb.SetStatusText(laserdata + ' File not found select a filename to open')
				laserdata = self._showOpenDialog("Select laser file to process", wildcard = "*laser.avi")
				if not laserdata:
					return
			self.laserMovie = ReadMovie(laserdata)
			self.laserMovie.getFrame()
			self.laserImage = self.laserMovie.getScaledBitmap(0.5)
			self.numframes = self.laserMovie.getNframes()
			self.laserScanLoaded = True
			self.frame = 1
			self.prevframe = 1
			self.percent = 1
			self.ctrpnl.cbpcapp.Show(True)
			self.ctrpnl.rbl.Show(True)
			self.ctrpnl.rbr.Show(True)

			print 'Num. Frames = ', self.laserMovie.getNframes()
			print 'Frame Rate = ', self.laserMovie.getFps(), ' frames per sec'
			self.sb.SetStatusText('Num. Frames = ' + str(self.laserMovie.getNframes()) + ' , ' + 'Frame Rate = ' + str(self.laserMovie.getFps()) + ' frames per sec')

	def OnStopProcess(self,e):
		self.stopProcessing()

	def stopProcessing(self):
		self.Processing = False
		self.textureMovie = None
		self.laserMovie = None
		self.textureScanLoaded = False
		self.laserScanLoaded = False
		self.preview3d.glCanvas.p.clear() # clear vertex GLbuffer memory
		self.ctrpnl.progressBar.SetValue(0)
		self.ctrpnl.progText2.SetLabel("")
		self.ctrpnl.stpprocButton.Show(False)
		self.ctrpnl.procButton.Show(True)
		self.Preview = True
		self.Refresh()

	def OnAppendPC(self, e):
		if not (self.Processing):
			if (e.IsChecked()):
				self.appendCloud = True
			else:
				self.appendCloud = False
		else:
			self.ctrpnl.cbpcapp.SetValue(False)
			print "ERROR: Currently Processing\n"
			self.sb.SetStatusText('ERROR: Currently Processing')
		
	def fillArray(self, cparray):
		for f in xrange (0, len(cparray)):
			for r in xrange (0, len(cparray[f])):
				thisColor = [0,0,0]
				thisPoint = [0,0,0]
				thisColor[0] = int(cparray[f][r][3])
				thisColor[1] = int(cparray[f][r][4])
				thisColor[2] = int(cparray[f][r][5])
				thisPoint[0] = float(cparray[f][r][0])
				thisPoint[1] = float(cparray[f][r][1])
				thisPoint[2] = float(cparray[f][r][2])
				self.preview3d.glCanvas.p.addPoint(thisPoint[0], thisPoint[2], thisPoint[1], thisColor[0]/255.0, thisColor[1]/255.0, thisColor[2]/255.0, 0.0)
				self.colorList.append(thisColor)
				self.pointList.append(thisPoint)
				wx.Yield()

	def testSpin(self, e):
		if (self.serialConnected and not self.Recording):
			self.serial.write('4')

	def processScanFrame(self):
		# code based on http://www.sjbaker.org/wiki/index.php?title=A_Simple_3D_Scanner
		#print "Proc frame " + str(self.frame) + "..\n"
		label = str(self.frame) + " of " + str(self.numframes)
		self.ctrpnl.progText2.SetLabel(label)
		if not (self.laserMovie.done()):
			if (self.frame > 1):
				self.laserMovie.getFrame()
				self.laserImage = self.laserMovie.getScaledBitmap(0.5)
			self.laserpil = self.laserMovie.getImg()
			if (self.textureScanLoaded):
				if not (self.textureMovie.done()):
					if (self.frame > 1):
						self.textureMovie.getFrame()
						self.textureImage = self.textureMovie.getScaledBitmap(0.5)
					self.texturepil = self.textureMovie.getImg()

			self.imwidth  = self.laserpil.GetWidth()
			self.imheight = self.laserpil.GetHeight()
			#print self.imwidth, self.imheight

			# all the points in this frame ie. this spline
			self.framePointList = []

			self.brightestX = 0
			self.brightestValue = 0

			#self.numframes = self.laserMovie.getNframes()

			if (self.frame == self.prevframe + int(math.ceil(self.numframes/100))):
				self.prevframe = self.frame
				self.percent += 1
				self.ctrpnl.progressBar.SetValue(self.percent)

			self.frameAngle = float(self.frame) * (360.0 / float(self.numframes))

			for y in xrange(0,self.imheight):
    				# find the brightest pixel
    				self.brightestValue = 0;
    				self.brightestX = -1;
    
    				for x in xrange(0,self.imwidth):
					#self.r = self.laserpil.GetRed(x,y)
					#self.g = self.laserpil.GetGreen(x,y)
					#self.b = self.laserpil.GetBlue(x,y)
      					#self.pixelValue = self.r + self.g + self.b     
      					#self.pixelBrightness = self.pixelValue
      					self.pixelBrightness = self.laserpil.GetRed(x,y)
      
      					if (self.pixelBrightness > self.brightestValue and self.pixelBrightness > self.threshold):
        					self.brightestValue = self.pixelBrightness;
        					self.brightestX = x;
    			
				#print "brightx: " + str(self.brightestX)
				#print "value: " + str(self.brightestValue)

				self.thisColor = [0,0,0]
				self.thisPoint = [0,0,0]
				#self.thisNormal = [0,0,0]
    
    				if (self.brightestX > 0):
					if (self.textureScanLoaded):
						if not (self.textureMovie.done()):
							self.thisColor[0] = int(self.texturepil.GetRed(self.brightestX,y))
							self.thisColor[1] = int(self.texturepil.GetGreen(self.brightestX,y))
							self.thisColor[2] = int(self.texturepil.GetBlue(self.brightestX,y))
							self.lastColor = self.thisColor
						else:
							self.thisColor = self.lastColor

						self.colorList.append(self.thisColor)

					self.laserpil.SetRGB(self.brightestX, y, 0, 255, 0)

					self.camAngle = camHFOV * (0.5 - float(self.brightestX) / float(self.imwidth))   
					self.pointAngle = 180.0 - self.camAngle + laserOffset
      					self.radius = camDistance * math.sin(self.camAngle * degreesToRadians) / math.sin(self.pointAngle * degreesToRadians)
    
					self.pointX = self.radius * math.sin(self.frameAngle * degreesToRadians) * self.sSide
					self.pointY = self.radius * math.cos(self.frameAngle * degreesToRadians)
					self.pointZ = -math.atan((camVFOV * degreesToRadians / 2.0)) * 2.0 * camDistance * float(y) / float(self.imheight)
					self.thisPoint[0] = self.pointX
					self.thisPoint[1] = self.pointY
					self.thisPoint[2] = self.pointZ
					self.pointList.append(self.thisPoint)

					# fix this
					#self.thisNormal[0] = self.pointX
					#self.thisNormal[1] = self.pointY
					#self.thisNormal[2] = 0.0
					#self.normalList.append(self.thisNormal)
					#print str(self.thisPoint[0]) + "," + str(self.thisPoint[1]) + "," + str(self.thisPoint[2]) + "," + str(self.thisNormal[0]) + "," + str(self.thisNormal[1]) + "," + str(self.thisNormal[2]) + "," + str(self.thisColor[0]) + "," + str(self.thisColor[1]) + "," + str(self.thisColor[2]) + "\n"
					if (self.textureScanLoaded):
						self.framePointList.append(self.thisPoint + self.thisColor)
						self.preview3d.glCanvas.p.addPoint(-1.0 * self.thisPoint[0], self.thisPoint[2], self.thisPoint[1], self.thisColor[0]/255.0, self.thisColor[1]/255.0, self.thisColor[2]/255.0, 0.0)
					else:
						self.framePointList.append(self.thisPoint +  [255.0, 255.0, 255.0])
						self.preview3d.glCanvas.p.addPoint(-1.0 * self.thisPoint[0], self.thisPoint[2], self.thisPoint[1], 0.5, 0.5, 0.5, 0.0)
				wx.Yield()
			self.laserScaled = self.laserpil.Scale((0.5 * self.imwidth), (0.5 * self.imheight), wx.IMAGE_QUALITY_HIGH)
			self.laserImage = wx.BitmapFromImage(self.laserScaled)
			self.cloudList.append(self.framePointList)
		return

	def serialList(self):
    		#scan for available ports. return a list of device names.
    		#return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
		if not glob.glob('/dev/ttyACM*'):
#		if not (glob.glob('/dev/ttyS*') + glob.glob('/dev/pts/*')):
			return ['None']
		return glob.glob('/dev/ttyACM*')
#		return glob.glob('/dev/ttyS*') + glob.glob('/dev/pts/*')

	def camList(self):
    		#scan for available cameras. return a list of device names.
		result = glob.glob('/dev/video*')
		if not result:
			return ['None']
		else:
			return result

	def _checkSerial(self):
		self._objLock.acquire()
		try:
			try:
				intNumChars = self.serial.inWaiting()
				if (intNumChars > 0):
					self.serialResponse = self.serial.readline(intNumChars)
			except:
				raise
		finally:
			self._objLock.release()

	def serialThread(self, e):
		self.SerThread = threading.Thread(target=self._checkSerial)
		self._objLock = threading.Lock()
		self.SerThread.start()

		if (self.serialResponse):
			print "RECEIVED: " + self.serialResponse + "\n"
			self.serialResponse = ""
			if (self.Recording):
    				self.Recording = False
    				self.writer = None
    				sleep(0.050)
    				if (self.recordingType == "laser"):
      					self.loadLaserScan()
					self.Laser(0, False)
    					self.Laser(1, False)
					self.ctrpnl.cbll.SetValue(False)
					self.ctrpnl.cblr.SetValue(False)
					self.sb.SetStatusText('Recording Finished' + '\t' + self.sb.GetStatusText())
    				elif (self.recordingType == "texture"):
					self.loadTextureScan()
					self.sb.SetStatusText('Recording Finished')
				self.ctrpnl.cbll.Show(True)
				self.ctrpnl.cblr.Show(True)
				self.ctrpnl.tsButton.Show(True)
				self.ctrpnl.absButton.Show(False)
				self.ctrpnl.textureButton.Show(True)
				self.ctrpnl.lslButton.Show(True)
				self.ctrpnl.lsrButton.Show(True)
				self.recordingType = ""

	def OnSetSerial(self, evt):
		eid = evt.GetId()
		if (eid == 10):
			self.sercfg.setBaud(evt.GetString())
		elif (eid == 20):
			self.sercfg.setBytes(evt.GetString())
		elif (eid == 30):
			self.sercfg.setParity(evt.GetString())
		elif (eid == 40):
			self.sercfg.setStop(evt.GetString())
		else:
			print "ERROR: Unknown event ID"

	def OnSlider(self, evt):
		eid = evt.GetId()
		cobj = evt.GetEventObject()
		if (eid == 5):
			self.brightness = cobj.GetValue()/100.0
			if (self.CamConnect):
				cv.SetCaptureProperty(self.capture, CV_CAP_PROP_BRIGHTNESS, self.brightness)
		elif (eid == 7):
			self.contrast = cobj.GetValue()/100.0
			if (self.CamConnect):
				cv.SetCaptureProperty(self.capture, CV_CAP_PROP_CONTRAST, self.contrast)

	def OnSetCfgVal(self, evt):
		eid = evt.GetId()
		cobj = evt.GetEventObject()
		print 'here'
		if (eid == 50):
			p = re.compile('[a-z,A-Z]+')
			if p.match(evt.GetString()):
				self.cfgValues[0] = evt.GetString()
				self.fileprefix = self.cfgValues[0]
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('file prefix must be alpha chars only')
		elif (eid == 55):
			p = re.compile('^[0-9]+\.[0-9]+$')
			if p.match(evt.GetString()):
				self.cfgValues[1] = evt.GetString()
				camHFOV = float(self.cfgValues[1])
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('HFOV must be float numeric chars only')
		elif (eid == 60):
			p = re.compile('^[0-9]+\.[0-9]+$')
			if p.match(evt.GetString()):
				self.cfgValues[2] = evt.GetString()
				camVFOV = float(self.cfgValues[2])
				camHFOV = (camVFOV * 3.75) / 5.0
				self.cfgValues[1] = str(camHFOV)
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('VFOV must be float numeric chars only')
		elif (eid == 65):
			p = re.compile('^[0-9]+\.[0-9]+$')
			if p.match(evt.GetString()):
				self.cfgValues[3] = evt.GetString()
				camDistance = float(self.cfgValues[3])
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('Cam Distance must be float numeric chars only')
		elif (eid == 70):
			p = re.compile('^[0-9]+\.[0-9]+$')
			if p.match(evt.GetString()):
				self.cfgValues[4] = evt.GetString()
				laserOffset = float(self.cfgValues[4])
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('Laser Angle must be float numeric chars only')
		elif (eid == 75):
			p = re.compile('^[0-9]+$')
			if p.match(evt.GetString()):
				self.cfgValues[5] = evt.GetString()
				self.threshold = float(self.cfgValues[5])
				self.sb.SetStatusText('')
			else:
				self.sb.SetStatusText('Threshold must be float numeric chars only')
		else:
			print "ERROR: Unknown event ID"	

class prevPcloud:
	def __init__(self, filename):
		cldfile = createWriter(filename)
		cldfile.openf()
		fd = cldfile.getfd()
		self.cplist = json.load(fd)

	def getSize(self):
		return len(self.cplist)

	def getarray(self):
		return self.cplist

if __name__ == '__main__':
	main()
