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

Sends jog commands to an Arduino running grbl

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


#serialEVT, EVT_SERIAL = wx.lib.newevent.NewEvent()          # this is the notification event to let us know the data has been updated
'''
Main window.  Creates all of the frames and binds buttons to functions.  Manages GUI
'''
class MainWindow(wx.Frame):
    def __init__(self, parent, title="Grbl_Jogger") :    
        self.parent = parent       
        mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(1024,768))         
        
        mainPanel = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)
        
        #   Build sizers and statusbar
        self.topSizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL) 
        
        self.rootSizer = wx.BoxSizer(wx.VERTICAL)          
                        
        self.CreateStatusBar()                              # statusbar in the bottom of the window                                  

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
 
        XPlusButton = wx.Button(mainPanel, -1, 'X+',size=(100,100))
        XMinusButton = wx.Button(mainPanel, -1, 'X-',size=(100,100))
        YPlusButton = wx.Button(mainPanel, -1, 'Y+',size=(100,100))
        YMinusButton = wx.Button(mainPanel, -1, 'Y-',size=(100,100))
        ZPlusButton = wx.Button(mainPanel, -1, 'Z+',size=(100,100))
        ZMinusButton = wx.Button(mainPanel, -1, 'Z-',size=(100,100))
        
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
        

        #   Bind events and buttons
#        self.Bind(EVT_SERIAL, self.updateText)                  # bind the event to a function
        self.Bind(wx.EVT_CLOSE, self.OnExit)
#        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        #self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
#        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
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
        
        self.distanceBox.SetValue('1')
        self.speedBox.SetValue('12')
        
        self.Layout()
	self.Show(True)
	
	
	
	try :
	  self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	  
	except :
	  self.showComError()
	  
	time.sleep(3)
	self.ser.flushInput()	
	self.ser.write("G20\n")
	
    def showComError(self) :     # Didn't find the board.  
        dlg = wx.MessageDialog(self, "Could not open COM port!", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
        self.OnExit(self)
        
    def showError(self) :     # Com Error
        dlg = wx.MessageDialog(self, "Bad Communications", 'Error!', wx.OK | wx.ICON_ERROR)  
        dlg.ShowModal()
      #  self.OnExit(self)
 
    def OnExit(self,e):         # stuff to do when the program is ending     
        global ser
        try :
	  self.ser.close()  
	except :
	  pass
        self.Destroy()              # wipe out windows and dump to the OS

    def XPlus (self, e) :   # # button one
      global x
      x = x + round(float(self.distanceBox.GetValue()), 6) 
      self.sendCommand('x')
     
    def XMinus (self, e) :
      global x
      x = x - round(float(self.distanceBox.GetValue()), 6) 
      self.sendCommand('x')
      
    def YPlus (self, e) :
      global y
      y = y + round(float(self.distanceBox.GetValue()), 6) 
      self.sendCommand('y')
    
    def YMinus (self, e) :
      global y
      y = y - round(float(self.distanceBox.GetValue()), 6) 
      self.sendCommand('y')
    
    def ZPLus(self, e) :
      global z
      z = z + round(float(self.distanceBox.GetValue()), 6) 
      self.sendCommand('z')
    
    def ZMinus(self, e) :
      global z
      z = z - round(float(self.distanceBox.GetValue()), 6)     
      self.sendCommand('z')
    
    def sendCommand(self, axis) :         
      speed = str(int(self.speedBox.GetValue()))
      speedCommand = "f" + speed + "\n"
      #self.ser.write("f" + +"\n")
      #print speedCommand
      #self.ser.write(speedCommand)
      if axis == 'x' :
	value = x
	
      if axis == 'y' :
	value = y

      if axis == 'z' :
	value = z
      dirCommand = "G0 " + "f" + speed + " " + axis + str(value) + "\n"
      #self.ser.write("G0 " + axis + " " + str(value) + '\n')
      print dirCommand
      self.ser.write(dirCommand)
      grbl_response = s.readline() # Wait for grbl response with carriage return
    

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()
