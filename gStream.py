#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl
"""

import serial
import time
import sys

sendIt = False

# Open grbl serial port
print "Opening port"
s = serial.Serial('/dev/ttyACM0',9600)
print "Port Opened!"

name = sys.argv[1]

# Open g-code file
f = open(name,'r');

commentsList = [';', '#', '(']

# Wake up grbl
s.write("\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
#s.write('G0z0x0y0')
s.flushInput()  # Flush startup text in serial input


# Stream g-code to grbl
for line in f:
  if len(line) > 1 :
    l = line.strip() # Strip all EOL characters for streaming  
    
    if not l[0] in commentsList :
      print 'Sending: ' + l,
      s.write(l + '\n') # Send g-code block to grbl
      grbl_out = s.readline() # Wait for grbl response with carriage return
      print ' : ' + grbl_out.strip()
      
    else :
      print "Comment: " + l
      



# Wait here until grbl is finished to close serial port and file.


# Close file and serial port
f.close()
s.close()
