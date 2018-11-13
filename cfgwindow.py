from __future__ import absolute_import

import wx

class NewWindow(wx.Frame):

    def __init__(self,parent,id,scfg,cfgval):
        wx.Frame.__init__(self, parent, id, 'Settings', size=(480,435), style=wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)
	self.parent = parent
	self.serialvalues = scfg.getvalues()
	self.cfgVal = cfgval
        wx.Frame.CenterOnScreen(self)
	self.Bind(wx.EVT_CLOSE, self.onClose)
	self.MakeModal(True)
	self.leftheaderLabel = wx.StaticText(self, -1, "-Scan Settings-")
	self.filePrefLabel = wx.StaticText(self, -1, "File Prefix:")
	self.filePrefix = wx.TextCtrl(self, 50, self.cfgVal[0], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.filePrefix.SetToolTip(wx.ToolTip("Enter a valid file prefix and hit enter"))
	self.brightLabel = wx.StaticText(self, -1, "Brightness:")
	self.brightsld = wx.Slider(self, 5, 0, 0, 100, wx.DefaultPosition, (250, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
	self.brightsld.SetToolTip(wx.ToolTip("Brightness of video frames."))
	self.contrastLabel = wx.StaticText(self, -1, "Contrast:")
	self.contrastsld = wx.Slider(self, 7, 12, -100, 100, wx.DefaultPosition, (250, -1), wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)
	self.contrastsld.SetToolTip(wx.ToolTip("Contrast of video frames."))
	self.contrastsld.SetTickFreq(5,1)
	self.camHFovLabel = wx.StaticText(self, -1, "Camera HFOV (Deg):")
	self.camHFov = wx.TextCtrl(self, 55, self.cfgVal[1], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.camHFov.SetToolTip(wx.ToolTip("Enter a valid floating point number between 10.0 and 90.0 and hit enter"))
	self.camVFovLabel = wx.StaticText(self, -1, "Camera VFOV (Deg):")
	self.camVFov = wx.TextCtrl(self, 60, self.cfgVal[2], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.camVFov.SetToolTip(wx.ToolTip("Enter a valid floating point number between 10.0 and 90.0 and hit enter"))
	self.camDistLabel = wx.StaticText(self, -1, "Camera Distance (mm):")
	self.camDist = wx.TextCtrl(self, 65, self.cfgVal[3], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.camDist.SetToolTip(wx.ToolTip("Enter a valid floating point number between 100.0 and 1200.0 and hit enter. This is the distance of the camera to the center of the turntable."))
	self.laserOffsetLabel = wx.StaticText(self, -1, "laser Offset (Deg):")
	self.laserOffset = wx.TextCtrl(self, 70, self.cfgVal[4], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.laserOffset.SetToolTip(wx.ToolTip("Enter a valid floating point number between 5.0 and 90.0 and hit enter. This is the angle of the laser to the camera."))
	self.thresholdLabel = wx.StaticText(self, -1, "Brighness Threshold:")
	self.thresholdValue = wx.TextCtrl(self, 75, self.cfgVal[5], size=(100, -1), style=wx.TE_PROCESS_ENTER)
	self.thresholdValue.SetToolTip(wx.ToolTip("Enter a valid number between 0 and 100 and hit enter. This is the level of brightness below which a pixel will be ignored."))
	#
	#baudList = self.parent.baudList()
	self.rightheaderLabel = wx.StaticText(self, -1, "-Serial Port Settings-")
	self.baudList = ['9600','19200','38400','57600','115200']
	self.baudLabel = wx.StaticText(self, -1, "Baud:")
	self.baudcombo = wx.ComboBox(self, 10, self.serialvalues[0], wx.DefaultPosition, (100,-1), self.baudList, wx.CB_DROPDOWN)
	self.baudcombo.SetToolTip(wx.ToolTip("select serial baudrate from dropdown-list"))
	self.byteList = ['Eight','Seven']
	self.byteLabel = wx.StaticText(self, -1, "Bits:")
	self.databytescombo = wx.ComboBox(self, 20, self.serialvalues[1], wx.DefaultPosition, (100,-1), self.byteList, wx.CB_DROPDOWN)
	self.databytescombo.SetToolTip(wx.ToolTip("select serial data bytes from dropdown-list"))
	self.parityList = ['None','Even','Odd']
	self.parityLabel = wx.StaticText(self, -1, "Parity:")
	self.paritycombo = wx.ComboBox(self, 30, self.serialvalues[2], wx.DefaultPosition, (100,-1), self.parityList, wx.CB_DROPDOWN)
	self.paritycombo.SetToolTip(wx.ToolTip("select serial parity from dropdown-list"))
	self.stopbitsList = ['One','Two']
	self.stopLabel = wx.StaticText(self, -1, "Stop bits:")
	self.stopbitscombo = wx.ComboBox(self, 40, self.serialvalues[3], wx.DefaultPosition, (100,-1), self.stopbitsList, wx.CB_DROPDOWN)
	self.stopbitscombo.SetToolTip(wx.ToolTip("select serial stop bits from dropdown-list"))

	self.sizer = wx.GridBagSizer()
	self.sizer.Add(self.leftheaderLabel, pos=(0,0), span=(1,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.filePrefLabel, pos=(1,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.filePrefix, pos=(1,1),flag=wx.ALL, border=5)
	self.sizer.Add(self.brightLabel, pos=(2,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.brightsld, pos=(3,0), span=(1,2), flag=wx.ALL, border=5)
	self.sizer.Add(self.contrastLabel, pos=(4,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.contrastsld, pos=(5,0), span=(1,2),flag=wx.ALL, border=5)
	self.sizer.Add(self.camHFovLabel, pos=(7,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.camHFov, pos=(7,1),flag=wx.ALL, border=5)
	self.sizer.Add(self.camVFovLabel, pos=(8,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.camVFov, pos=(8,1),flag=wx.ALL, border=5)
	self.sizer.Add(self.camDistLabel, pos=(9,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.camDist, pos=(9,1),flag=wx.ALL, border=5)
	self.sizer.Add(self.laserOffsetLabel, pos=(10,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.laserOffset, pos=(10,1),flag=wx.ALL, border=5)
	self.sizer.Add(self.thresholdLabel, pos=(11,0),flag=wx.ALL, border=5)
	self.sizer.Add(self.thresholdValue, pos=(11,1),flag=wx.ALL, border=5)
	#
	self.sizer.Add(self.rightheaderLabel, pos=(0,4), span=(1,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.baudLabel, pos=(1,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.baudcombo, pos=(1,4),flag=wx.ALL, border=5)
	self.sizer.Add(self.byteLabel, pos=(2,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.databytescombo, pos=(2,4),flag=wx.ALL, border=5)
	self.sizer.Add(self.parityLabel, pos=(3,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.paritycombo, pos=(3,4),flag=wx.ALL, border=5)
	self.sizer.Add(self.stopLabel, pos=(4,3),flag=wx.ALL, border=5)
	self.sizer.Add(self.stopbitscombo, pos=(4,4),flag=wx.ALL, border=5)

	self.Bind(wx.EVT_SLIDER, self.parent.OnSlider, self.brightsld)
	self.Bind(wx.EVT_SLIDER, self.parent.OnSlider, self.contrastsld)
	self.Bind(wx.EVT_COMBOBOX, self.parent.OnSetSerial, self.baudcombo)
	self.Bind(wx.EVT_COMBOBOX, self.parent.OnSetSerial, self.databytescombo)
	self.Bind(wx.EVT_COMBOBOX, self.parent.OnSetSerial, self.paritycombo)
	self.Bind(wx.EVT_COMBOBOX, self.parent.OnSetSerial, self.stopbitscombo)

	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.filePrefix)
	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.camHFov)
	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.camVFov)
	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.camDist)
	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.laserOffset)
	self.Bind(wx.EVT_TEXT_ENTER, self.parent.OnSetCfgVal, self.thresholdValue)

	self.SetSizer(self.sizer)
	self.Layout()

    def onClose(self, event):
        """
        Make the frame non-modal as it closes to re-enable other windows
        """
        self.MakeModal(False)
        self.Destroy()

