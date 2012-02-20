'''
Written by Jesse Merritt
October 1, 2011

   This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Sends jog commands to an Arduino running grbl.  Builds a very simple G-Code string and 
sends it to the controller.  Only one move at a time is supported although the controller
will buffer commands.

Here is an awesome wx tutorial I cam acoss while writing this:
http://wiki.wxpython.org/AnotherTutorial

The GUI requires WX.

The program depends on the following modules:
serial:	Controls data over the virtual serial port
wx:  	Manages the GUI
wx.lib.newevent:  Event manager

Change Log:
------------------------------------------------------------------------------------------------------


'''
import serial 
import wx
import sys
import os
import time

version = "0.1"

x = 0	# Location of X Axis
y = 0	# Location of Y Axis
z = 0	# Location of Z Axis
  
class MainWindow(wx.Frame):
    def __init__(self, parent, title="Grbl_Jogger") :   
        self.parent = parent 
        self.dirname = '.' 
  
    #	Read Configuration from file
        self.cfg = wx.Config('grblJoggerConfig')
        if self.cfg.Exists('port'):
	  print "Reading Configuration"
          self.port = self.cfg.Read('port')
          self.baud = self.cfg.ReadInt('baud')
        else:
          self.port = '/dev/ttyACM0'
          self.baud = 9600
          print "Creating config"
          self.cfg.Write("port", self.port)
          self.cfg.WriteInt("baud", self.baud)


	print "using port " + self.port
	print "using baud " + str(self.baud)
	
	mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(2048,600))    
        
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar       
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.
      
	menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        
        menuSave = filemenu.Append(wx.ID_SAVE, "Save", "Save the current data")     
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")     
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  
        
        self.jogPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)       
        #self.editorPanel1 = wx.Panel(self, -1, style = wx.SUNKEN_BORDER)
        #self.editorPanel2 = wx.Panel(self, -1, style = wx.SUNKEN_BORDER)
        #self.editorPanel3 = wx.Panel(self, -1, style = wx.SUNKEN_BORDER)
        
        #   Build sizers and statusbar
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttonSizer2 = wx.BoxSizer(wx.VERTICAL)
        self.editorSizer1 = wx.BoxSizer(wx.VERTICAL) 
        self.editorSizer2 = wx.BoxSizer(wx.HORIZONTAL)      
        #self.editorSizer3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)                        
        self.statusBar = self.CreateStatusBar()                              # statusbar in the bottom of the window    
        
        #	Input boxes for distance and speed
        self.distanceLabel = wx.StaticText(self.jogPanel, 1, "Distance:")
        self.distanceBox = wx.TextCtrl(self.jogPanel)    
        
        self.speedLabel = wx.StaticText(self.jogPanel, 1, "IPM:")
        self.speedBox = wx.TextCtrl(self.jogPanel)    
        

        
        #	Buttons;  One per direction
        XPlusButton = wx.Button(self.jogPanel, -1, 'X+',size=(75,75))
        XMinusButton = wx.Button(self.jogPanel, -1, 'X-',size=(75,75))
        YPlusButton = wx.Button(self.jogPanel, -1, 'Y+',size=(75,75))
        YMinusButton = wx.Button(self.jogPanel, -1, 'Y-',size=(75,75))
        ZPlusButton = wx.Button(self.jogPanel, -1, 'Z+',size=(75,75))
        ZMinusButton = wx.Button(self.jogPanel, -1, 'Z-',size=(75,75))        
        setHomeButton = wx.Button(self.jogPanel, -1, 'Set Home')     
        resetButton = wx.Button(self.jogPanel, -1, 'Reset Controller') 
        
        self.codeViewer = wx.TextCtrl(self.jogPanel, -1, '', style=wx.TE_MULTILINE|wx.VSCROLL)
        startButton = wx.Button(self.jogPanel, -1, 'Start')
        stopButton = wx.Button(self.jogPanel, -1, 'Stop')
        pauseButton = wx.Button(self.jogPanel, -1, 'Pause')
        
        

        #  Sizers.  Everything is on rootSizer         
        self.topSizer.Add(self.distanceLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.distanceBox, 1)
        self.topSizer.Add(self.speedLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.speedBox, 1)        
        self.buttonSizer.Add(XPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(XMinusButton,1, wx.EXPAND)
        self.buttonSizer.Add(YPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(YMinusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(ZPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(ZMinusButton, 1, wx.EXPAND)         
        self.buttonSizer2.Add(setHomeButton, 1, wx.EXPAND)
        self.buttonSizer2.Add(resetButton, 1, wx.EXPAND)
        
        self.editorSizer1.Add(self.codeViewer, 1, wx.EXPAND)      
        self.editorSizer2.Add(startButton, 1, wx.EXPAND)
        self.editorSizer2.Add(stopButton, 1, wx.EXPAND)
        self.editorSizer2.Add(pauseButton, 1, wx.EXPAND)
        
        self.rootSizer.Add(self.topSizer, 1, wx.EXPAND)
        self.rootSizer.Add(self.buttonSizer, 1, wx.EXPAND)   
        self.rootSizer.Add(self.buttonSizer2, 1, wx.EXPAND) 
        self.rootSizer.Add(self.editorSizer1, 3, wx.EXPAND)        
        self.rootSizer.Add(self.editorSizer2, 1, wx.EXPAND)
       
       # self.rootSizer.Add(self.editorSizer3, 1, wx.EXPAND)


	#	Bind events to buttons
        self.Bind(wx.EVT_CLOSE, self.onExit)
        
#       self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
#       self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        self.Bind(wx.EVT_BUTTON, self.XPlus, XPlusButton)
        self.Bind(wx.EVT_BUTTON, self.XMinus, XMinusButton)
        self.Bind(wx.EVT_BUTTON, self.YPlus, YPlusButton)
        self.Bind(wx.EVT_BUTTON, self.YMinus, YMinusButton)
        self.Bind(wx.EVT_BUTTON, self.ZPLus, ZPlusButton)
        self.Bind(wx.EVT_BUTTON, self.ZMinus, ZMinusButton)
        
        self.Bind(wx.EVT_BUTTON, self.setHome, setHomeButton)
        self.Bind(wx.EVT_BUTTON, self.resetController, resetButton)
        
        self.Bind(wx.EVT_BUTTON, self.onStart, startButton)
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)
        self.Bind(wx.EVT_BUTTON, self.onPause, pauseButton)
        
        

        # set the sizers
        self.SetSizer(self.rootSizer)
        self.SetAutoLayout(1)
        self.rootSizer.Fit(self)     
        
        #	Set preset values
        self.distanceBox.SetValue('1')
        self.speedBox.SetValue('12')
        
        self.Layout()
	self.Show(True)	
	
	try :
	  self.ser = serial.Serial(self.port, self.baud, timeout=1)
	  time.sleep(2)			# Give Grbl time to come up and respond
	  
	except :
	  self.showComError()
	  
	
	try :
	  self.ser.flushInput()		# Dump all the initial Grbl stuff	
	  self.ser.write("G20\n")		# yeah, we only use this in the US.  Everyone else should make this metric
	  
	except :
	  pass
	
    def onOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.codeViewer.SetValue(f.read())
            f.close()
        dlg.Destroy()
	
    def onStart(self, e) :
      print "Start"
      
    def onSave(self, e) :
      print "Save G-Code"
      
    def onPause(self, e) :
      print "Pause"
    
    def onStop(self, e) :
      print "Stop"
      
    def setHome(self, e) :
      print "set home"
      
    def resetController(self, e) :
      print "reset Controller"
    
    
    def showComError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        #self.onExit(self)	#	Dump out
        
    def showComWriteError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Error writing to Com port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        
    def showComTimeoutError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Controller did not respond!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal() 
        
    def showValueError(self) :	#	General error.  Not really implemented
        dlg = wx.MessageDialog(self, "I need a number!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
 
    def onExit(self,e):         # stuff to do when the program is ending     
        global ser
        try :
	  self.ser.close()  	# Needs to be in a try in case it wasn't opened
	except :
	  pass
	
        self.Destroy()              # wipe out window and dump to the OS
        
    def readDistance(self) :
      try :
	d = abs(round(float(self.distanceBox.GetValue()), 6))
      	return d
      	
      except :	
	self.showValueError()      

    def XPlus (self, e) :  	#	Increment X
      global x
      x = x + self.readDistance()
      self.sendCommand('x')
     
    def XMinus (self, e) :	#	Decrement X
      global x
      x = x - self.readDistance()
      self.sendCommand('x')
      
    def YPlus (self, e) :	#	Increment Y
      global y
      y = y + self.readDistance()
      self.sendCommand('y')
    
    def YMinus (self, e) :	#	Decrement Y
      global y
      y = y - self.readDistance()
      self.sendCommand('y')
    
    def ZPLus(self, e) :	#	Increment Z
      global z
      z = z + self.readDistance()
      self.sendCommand('z')
    
    def ZMinus(self, e) :	#	Decrement Z
      global z
      z = z - self.readDistance()
      self.sendCommand('z')
    
    def sendCommand(self, axis) :   
      try :
	speed = str(int(self.speedBox.GetValue()))
	speedCommand = "f" + speed + "\n"  
	
      except  :
	self.showValueError()	
       
      if axis == 'x' :
	value = x
	
      if axis == 'y' :
	value = y

      if axis == 'z' :
	value = z
	
      dirCommand = "G0 " + "f" + speed + " " + axis + str(value) + "\n"
      
      try :
	self.ser.write(dirCommand)
      except :
	self.showComWriteError()
      
      grbl_response = self.ser.readline() 	# Wait for grbl response with carriage return       
      self.statusBar.SetStatusText("Sent: " + dirCommand.strip() + ": " + "\tReceived: " +grbl_response)
      
      if not grbl_response :
	self.showComTimeoutError()
    

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()
