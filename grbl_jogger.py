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
import  wx.lib.newevent

version = "0.1"

x = 0	# Location of X Axis
y = 0	# Location of Y Axis
z = 0	# Location of Z Axis


ser = serial.Serial()

  
serialEVT, EVT_SERIAL = wx.lib.newevent.NewEvent()  

class MainWindow(wx.Frame):
    def __init__(self, parent, title="Grbl_Jogger") : 	
	global ser
	
        self.parent = parent 
        self.dirname = '.' 
        
	
		
	#print "using port " + port
	#print "using baud " + str(baud)
	
	mainFrame = wx.Frame.__init__(self,self.parent, title=title, size=(2048,600))   
        
        filemenu= wx.Menu()
        setupmenu = wx.Menu()
        helpmenu = wx.Menu()

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")                    # Adding the "filemenu" to the MenuBar   
        menuBar.Append(setupmenu, "Setup")
        menuBar.Append(helpmenu, "Help")
        self.SetMenuBar(menuBar)                            # Adding the MenuBar to the Frame content.
        
        menuPorts = setupmenu.Append(wx.ID_NEW, "Select Port", "Configure serial port");
      
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
        self.Bind(wx.EVT_MENU, self.setupPort, menuPorts)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        self.Bind(wx.EVT_BUTTON, self.XPlus, XPlusButton)
        self.Bind(wx.EVT_BUTTON, self.XMinus, XMinusButton)
        self.Bind(wx.EVT_BUTTON, self.YPlus, YPlusButton)
        self.Bind(wx.EVT_BUTTON, self.YMinus, YMinusButton)
        self.Bind(wx.EVT_BUTTON, self.ZPlus, ZPlusButton)
        self.Bind(wx.EVT_BUTTON, self.ZMinus, ZMinusButton)
        
        self.Bind(wx.EVT_BUTTON, self.setHome, setHomeButton)
        self.Bind(wx.EVT_BUTTON, self.resetController, resetButton)
        
        self.Bind(wx.EVT_BUTTON, self.onStart, startButton)
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)
        self.Bind(wx.EVT_BUTTON, self.onPause, pauseButton)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)    
        

        # set the sizers
        self.SetSizer(self.rootSizer)
        self.SetAutoLayout(1)
        self.rootSizer.Fit(self)     
        
        #	Set preset values
        self.distanceBox.SetValue('1')
        self.speedBox.SetValue('12')
        
        self.Layout()
	self.Show(True)	
	
	#Read Configuration from file
        self.cfg = wx.Config('grblJoggerConfig')
        if self.cfg.Exists('port'):
	  print "Reading Configuration"
	  port.name = self.cfg.Read('port')
	  port.baud = self.cfg.ReadInt('baud') 
	  port.timeout = self.cfg.ReadInt('timeout')
        
        else:
	  print "No config"
         # self.cfg.Write("port", port)
         # self.cfg.WriteInt("baud", baud)
	
	try :
	  #ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	  ser = serial.Serial(port.name, port.baud, timeout=port.timeout)
	  #self.ser = serial.Serial(port.name, port.baud, timeout = port.timeout)
	  time.sleep(2)			# Give Grbl time to come up and respond
	  ser.flushInput()		# Dump all the initial Grbl stuff	
	  ser.write("G20\n")		# yeah, we only use this in the US.  Everyone else should make this metric
	  
	except :
	  self.showComError()  
	  
	

	
    def OnKeyDown(self, event):
      global x
      global y
      global z
      keycode = event.GetKeyCode()
      #print keycode
      if keycode == wx.WXK_ESCAPE:
        ret  = wx.MessageBox('Are you sure to quit?', 'Question', 
	wx.YES_NO | wx.NO_DEFAULT, self)
        if ret == wx.YES:
	  self.Close()
	  
      if keycode == 315 :	#	Up Arrow
	self.YPlus(None)
	
      if keycode == 317 :	#	Down Arrow
	self.YMinus(None)
	
      if keycode == 314 :	#	Left Arrow
	self.XMinus(None)
	
      if keycode == 316 :	#	Right Arrow
	self.XPlus(None)
	
      if keycode == 366 :	#	Page UP
	self.ZPlus(None)
	
      if keycode == 367 :	#	Page Down
	self.ZMinus(None)
      
      event.Skip()
	
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
        
    def setupPort(self, e) :        
      dia = configSerial(self, -1)
      dia.ShowModal()
      self.portIsConfigured = 1
      dia.Destroy() 
	
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
        self.setupPort(None)
        
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
	  ser.close()  	# Needs to be in a try in case it wasn't opened
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
    
    def ZPlus(self, e) :	#	Increment Z
      global z
      z = z + self.readDistance()
      self.sendCommand('z')
    
    def ZMinus(self, e) :	#	Decrement Z
      global z
      z = z - self.readDistance()
      self.sendCommand('z')
    
    def sendCommand(self, axis) :   
      global ser
      
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
	ser.write(dirCommand)
      except :
	self.showComWriteError()
      
      grbl_response = ser.readline() 	# Wait for grbl response with carriage return       
      self.statusBar.SetStatusText("Sent: " + dirCommand.strip() + ": " + "\tReceived: " +grbl_response)
      
      print grbl_response
      if not grbl_response :
	self.showComTimeoutError()
    

class configSerial(wx.Dialog):
    def __init__(self, parent, id, title = "Configure Serial Port"):
        global ser

	self.parent= parent
	self.id = id

        if ser.isOpen() :  # Dump the port if already open
	  print "Closing port that's already open"
          ser.close()

        self.comError = 0;
        self.ports = []
        self.ports = self.findPorts()
        if len(self.ports) < 1 :
            self.ports.append("No Ports Found")
            
        self.baudRates = ['110', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200', '28800', '38400', '56000', '57600', '115200']
        self.dataBitsList = ['5', '6', '7', '8']
        self.parityList = ['Even', 'Odd', 'N']
        self.stopBitsList = ['1','2']
        self.flowControlList = ['XON', 'XOFF', 'Hardware', 'None']

        # Init to defaults
        self.port = self.ports[0]
        self.baud = '9600'
        self.dataBits = '8'
        self.parity = 'N'
        self.stopBit = '1'
        self.flowControl = 'None'

        #   Build the box
        wx.Dialog.__init__(self, self.parent, self.id, title, size=(225,325)) # second is vertical

        #   Vertical sizer with a bunch of horizontal sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer7 = wx.BoxSizer(wx.HORIZONTAL)        
      
        sizer.Add(sizer2, 0, wx.EXPAND)
        sizer.Add(sizer3, 0, wx.EXPAND)
        sizer.Add(sizer4, 0, wx.EXPAND)
        sizer.Add(sizer5, 0, wx.EXPAND)
        sizer.Add(sizer6, 0, wx.EXPAND)
        sizer.Add(sizer7, 0, wx.EXPAND)        

        #   Drop downs and text
        st1 = sizer2.Add(wx.StaticText(self, -1, 'Port', style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 1, wx.EXPAND)
        self.portsCombo = wx.ComboBox(self, -1, self.ports[0], size=(150, -1), choices=self.ports,style=wx.CB_READONLY)
        portsBox = sizer2.Add(self.portsCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        st2 = sizer3.Add(wx.StaticText(self, -1, 'Baud', style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL ), 1, wx.EXPAND)
        self.baudCombo = wx.ComboBox(self, -1, self.baud, size=(150, -1), choices=self.baudRates,style=wx.CB_READONLY)
        baudBox = sizer3.Add(self.baudCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        st3 = sizer4.Add(wx.StaticText(self, -1, 'Data Bits', style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 1, wx.EXPAND)
        self.bitsCombo = wx.ComboBox(self, -1, self.dataBits, size=(150, -1), choices=self.dataBitsList,style=wx.CB_READONLY)
        bitsBox = sizer4.Add(self.bitsCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        st4 = sizer5.Add(wx.StaticText(self, -1, 'Parity', style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 1, wx.EXPAND)
        self.parityCombo = wx.ComboBox(self, -1, self.parity,  size=(150, -1), choices=self.parityList,style=wx.CB_READONLY)
        parityBox = sizer5.Add(self.parityCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        st5 = sizer6.Add(wx.StaticText(self, -1, 'Stop Bits', style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL), 1, wx.EXPAND)
        self.stopCombo = wx.ComboBox(self, -1, self.stopBit, size=(150, -1), choices=self.stopBitsList,style=wx.CB_READONLY)
        stopBox = sizer6.Add(self.stopCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        st6 = sizer7.Add(wx.StaticText(self, -1, 'Flow Control', style=wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL), 1, wx.EXPAND)
        self.flowCombo = wx.ComboBox(self, -1, self.flowControl, size=(150, -1), choices=self.flowControlList,style=wx.CB_READONLY)
        flowBox = sizer7.Add(self.flowCombo, 0, wx.ALL| wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)        
        
   
        autoButton = wx.Button(self, -1, 'Auto-Config')
        sizer.Add(autoButton, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        doneButton = wx.Button(self, -1, 'Done')
        sizer.Add(doneButton, 0, wx.ALL|wx.ALIGN_CENTER, 5)  
        
        self.Bind(wx.EVT_BUTTON, self.done,doneButton)
        self.Bind(wx.EVT_BUTTON, self.autoDetect,autoButton)

        self.SetSizer(sizer)


    def done(self, e) :
        global ser	
        port.name = self.portsCombo.GetValue()
        port.baud = int(self.baudCombo.GetValue())
        port.dataBits = int(self.bitsCombo.GetValue())
        port.parity = self.parityCombo.GetValue()
        port.stopBit = int(self.stopCombo.GetValue())
        self.flowControl = self.flowCombo.GetValue()

        port.rtscts = 0
        port.xonxoff = 0

        if self.flowControl == "Hardware" :
            port.rtscts = 1

        if self.flowControl == "None" :
            port.rtscts = 0                

        if self.ports != "No Ports Found" :
           #ser = serial.Serial(port= port.name, baudrate= port.baud, bytesize=port.dataBits, parity= port.parity,\
           # stopbits=port.stopBit, timeout = None, xonxoff= port.xonxoff, rtscts=port.rtscts)
           #ser = serial.Serial(port.name, baudrate=port.baud, timeout=port.timeout)
           ser = serial.Serial('/dev/ttyACM0', 9600, timeout=2)

           if ser.isOpen() :
	      print "Yay from config"
	      
	self.cfg.Write("port", port.name)
        self.cfg.WriteInt("baud", port.baud)
          
        print "Name: " + port.name
        port.reset()
		
        self.Close(True)
                
        
    def autoDetect(self, e) :
        print "To be added"

    def findPorts(self) :    
	global ser
        self.ports = []
        for i in range(25) :  #  Windows
            try :                
                s = serial.Serial("COM" + str(i))                
                s.close()
                self.ports.append("COM" + str(i))                
            except :
                pass
            
        if len(self.ports) > 0 : 
            return self.ports

	for i in range(25) :
	  for k in ["/dev/ttyUSB", "/dev/ttyACM", "/dev/ttyS"] : # Linux
            try :		
                s = serial.Serial(k+str(i))
                s.close()                
                self.ports.append(k+ str(i))

            except :
                pass
                
        return self.ports  
        
class Port() :		# Dummy class to encapsulate the serial port attributes;  Cleaner than global  also a couple of helper methods
  def __init__(self) :     
    self.name = '/dev/ttyACM0'
    self.baud = 0
    self.dataBits = 8
    self.parity = 'n'
    self.stopBits = 1
    self.timeout = 1
    self.rtscts = 0
    
  
  def reset(self) :
    global ser
    ser.flushInput()
    time.sleep(2)
    
port = Port()

app = wx.App(False)         # wx instance
frame = MainWindow(None)    # main window frame

app.MainLoop()
