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
        mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(800,600))         
        
        mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        #   Build sizers and statusbar
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)         
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)                        
        self.statusBar = self.CreateStatusBar()                              # statusbar in the bottom of the window                                  

        # Setting up the menus
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()       

        menuSave = filemenu.Append(wx.ID_SAVE, "Save", "Save the current data")     
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")     
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")  

        # Menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar       
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.
 
	#	Buttons;  One per direction
        XPlusButton = wx.Button(mainPanel, -1, 'X+',size=(75,75))
        XMinusButton = wx.Button(mainPanel, -1, 'X-',size=(75,75))
        YPlusButton = wx.Button(mainPanel, -1, 'Y+',size=(75,75))
        YMinusButton = wx.Button(mainPanel, -1, 'Y-',size=(75,75))
        ZPlusButton = wx.Button(mainPanel, -1, 'Z+',size=(75,75))
        ZMinusButton = wx.Button(mainPanel, -1, 'Z-',size=(75,75))
        
        #	Input boxes for distance and speed
        self.distanceLabel = wx.StaticText(mainPanel, 1, "Distance:")
        self.distanceBox = wx.TextCtrl(self)
        self.speedLabel = wx.StaticText(mainPanel, 1, "IPM:")
        self.speedBox = wx.TextCtrl(self)

        #  Sizers.  Everything is on rootSizer         
        self.topSizer.Add(self.distanceLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.distanceBox, 2, wx.EXPAND)
        self.topSizer.Add(self.speedLabel, 1, wx.EXPAND)
        self.topSizer.Add(self.speedBox, 2, wx.EXPAND)        
        self.buttonSizer.Add(XPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(XMinusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(YPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(YMinusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(ZPlusButton, 1, wx.EXPAND)
        self.buttonSizer.Add(ZMinusButton, 1, wx.EXPAND)                 
        self.rootSizer.Add(self.topSizer, 1, wx.EXPAND)
        self.rootSizer.Add(self.buttonSizer, 4, wx.EXPAND)       

	#	Bind events to buttons
        self.Bind(wx.EVT_CLOSE, self.OnExit)
#       self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
#       self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
#       self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_BUTTON, self.XPlus, XPlusButton)
        self.Bind(wx.EVT_BUTTON, self.XMinus, XMinusButton)
        self.Bind(wx.EVT_BUTTON, self.YPlus, YPlusButton)
        self.Bind(wx.EVT_BUTTON, self.YMinus, YMinusButton)
        self.Bind(wx.EVT_BUTTON, self.ZPLus, ZPlusButton)
        self.Bind(wx.EVT_BUTTON, self.ZMinus, ZMinusButton)

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
	  self.ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
	  
	except :
	  self.showComError()
	  
	time.sleep(3)
	self.ser.flushInput()	
	self.ser.write("G20\n")
	
	
	
    def showComError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        self.OnExit(self)	#	Dump out
        
    def showComWriteError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Error writing to Com port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        
    def showComTimeoutError(self) :     #	Can't open COM port
        dlg = wx.MessageDialog(self, "Controller did not respond!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal() 
        
    def showValueError(self) :	#	General error.  Not really implemented
        dlg = wx.MessageDialog(self, "I need a number!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
 
    def OnExit(self,e):         # stuff to do when the program is ending     
        global ser
        try :
	  self.ser.close()  	# Needs to be in a try in case it wasn't opened
	except :
	  pass
	
        self.Destroy()              # wipe out windows and dump to the OS
        
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
      #print 
      
      self.statusBar.SetStatusText("Sent: " + dirCommand.strip() + ": " + "\tReceived: " +grbl_response)
      
      if not grbl_response :
	self.showComTimeoutError()
    

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()
