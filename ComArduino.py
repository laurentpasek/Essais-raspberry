# 19 July 2014

# in case any of this upsets Python purists it has been converted from an equivalent JRuby program

# this is designed to work with ... ArduinoPC2.ino ...

# the purpose of this program and the associated Arduino program is to demonstrate a system for sending 
#   and receiving data between a PC and an Arduino.

# The key functions are:
#    sendToArduino(str) which sends the given string to the Arduino. The string may 
#                       contain characters with any of the values 0 to 255
#
#    recvFromArduino()  which returns an array. 
#                         The first element contains the number of bytes that the Arduino said it included in
#                             message. This can be used to check that the full message was received.
#                         The second element contains the message as a string


# the overall process followed by the demo program is as follows
#   open the serial connection to the Arduino - which causes the Arduino to reset
#   wait for a message from the Arduino to give it time to reset
#   loop through a series of test messages
#      send a message and display it on the PC screen
#      wait for a reply and display it on the PC

# to facilitate debugging the Arduino code this program interprets any message from the Arduino
#    with the message length set to 0 as a debug message which is displayed on the PC screen

# the message to be sent to the Arduino starts with < and ends with >
#    the message content comprises a string, an integer and a float
#    the numbers are sent as their ascii equivalents
#    for example <LED1,200,0.2>
#    this means set the flash interval for LED1 to 200 millisecs
#      and move the servo to 20% of its range

# receiving a message from the Arduino involves
#    waiting until the startMarker is detected
#    saving all subsequent bytes until the end marker is detected

# NOTES
#       this program does not include any timeouts to deal with delays in communication
#
#       for simplicity the program does NOT search for the comm port - the user must modify the
#         code to include the correct reference.
#         search for the lines 
#               serPort = "/dev/ttyS80"
#               baudRate = 9600
#               ser = serial.Serial(serPort, baudRate)
#


#=====================================

#  Function Definitions

#=====================================

def sendToArduino(sendStr):
  ser.write(sendStr)
#  print ("envoye par sendToArduino" + sendStr )


#======================================

def recvFromArduino():
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  byteCount = -1 # to allow for the fact that the last increment will be one too many
  
  # wait for the start character
  while  ord(x) != startMarker: 
    x = ser.read()
  
  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) != startMarker:
      ck = ck + x 
      byteCount += 1
    x = ser.read()
  
  return(ck)
#  print (ck)


#============================

def waitForArduino():

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

      while ser.inWaiting() == 0:
        pass
        
      msg = recvFromArduino()

      print (msg)
      time.sleep(2)
      print ()
      
#======================================

def runTest(td):
  numLoops = len(td)
  waitingForReply = False

  n = 0
  while n < numLoops:

    teststr = td[n]

    if waitingForReply == False:
      sendToArduino(teststr)
      print ("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
      waitingForReply = True

    if waitingForReply == True:

      while ser.inWaiting() == 0:
        pass
        
      dataRecvd = recvFromArduino()
      print ("Reply Received  " + dataRecvd)
      n += 1
      waitingForReply = False

      print ("===========")

#    time.sleep(2)

#======================================
def lectureCapteurs ():
    capteurs = []
    capteurs.append ("<LireTempEau>")
    capteurs.append ("<LireTempAir>")
    capteurs.append ("<LireHygro>")
    capteurs.append ("<LirePression>")
    capteurs.append ("<LireTempElec>")
    capteurs.append ("<LireLuminosite>")
    numloops = len (capteurs)
    n = 0
    
    while n < numloops :
        testString = capteurs [n]
        sendToArduino (testString)
        
#        print ("ordre envoye a l'arduino" + testString)
        
        n += 1
        time.sleep (2)
        
#======================================
        
def collecteDonnees ():
    global Teau, Tair, Hygro, Pression, Telec, Luminosite
    
    Teau = float(receptionDonnees ("<SendTempEau>"))
    Tair = float(receptionDonnees ("<SendTempAir>"))
    Hygro = float(receptionDonnees ("<SendHygro>"))
    Pression = float(receptionDonnees ("<SendPression>"))
    Telec = float(receptionDonnees ("<SendTempElec>"))
    Luminosite = float(receptionDonnees ("<SendLuminosite>"))
    
    
#======================================
    
def receptionDonnees (testString):
    waitingForReply = False
    if waitingForReply == False :
        sendToArduino (testString)
        waitingForReply = True
    
    if waitingForReply == True :
        while ser.inWaiting () == 0 :
            pass
        
        dataReceived = recvFromArduino ()
        waitingForReply = False
#        print ("recu par pi : " +dataReceived)
        return (dataReceived)


#======================================


def versInfluxDB () :
    global Teau, Tair, Hygro, Telec, Pression, Luminosite
    
    json_body = [
        {
            "measurement": "Temp_Air",
            "tags": {
                "mesure": "temperature",
                "milieu": "air"
                },
            "fields": {
                "temperature": Tair
                }
            },
        {
            "measurement": "Hygro",
            "tags": {
                "mesure": "hygrometrie",
                "milieu": "air"
                },
            "fields": {
                "hygrometrie": Hygro
                }
            },
        {
            "measurement": "Temp_Eau",
            "tags": {
                "mesure": "temperature",
                "milieu": "eau"
                },
            "fields": {
                "temperature": Teau
                }
            },
	{
	    "measurement": "Temp_Elec",
	    "tags": {
	        "mesure": "temperature",
	        "milieu": "air_coffret_electronique"
	        },
	    "fields": {
	        "temperature": Telec
	        }
	    },
	{
	    "measurement": "Pression_atmospherique",
	    "tags": {
	        "mesure": "pression",
	        "milieu": "air"
	        },
	    "fields": {
	        "pression": Pression
	        }
	    },
	{
	    "measurement": "Luminosite",
	    "tags": {
		"mesure": "luminosite",
		"milieu": "air"
		},
	    "fields": {
		"luminosite": Luminosite
		}
	    },
        
        ]
    
    client.write_points(json_body)
    


#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import serial
import time
from influxdb import InfluxDBClient
import datetime

print ()
print ()

# NOTE the user must ensure that the serial port and baudrate are correct
#serPort = "/dev/ttyS80"
serPort = "/dev/ttyUSB0"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)

print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))


startMarker = 60
endMarker = 62

Teau = 0
Tair = 10
Hygro = 0
Pression = 0
Telec = 0
Luminosite = 0


client = InfluxDBClient (host='localhost', port=8086)
client.switch_database('hydro')



#waitForArduino()

while True :
  
#  testData = []
  #testData.append("<LED1,200,0.2>")
  #testData.append("<LED1,800,0.7>")
  #testData.append("<LED2,800,0.5>")
  #testData.append("<LED2,200,0.2>")
  #testData.append("<LED1,200,0.7>")
#  testData.append("<T.air>")
#  testData.append("<T.eau>")
#  testData.append("<Hygro>")
  #testData.append("<temperature>")


#  runTest(testData)

#  print (Teau)
#  print ()
  
  lectureCapteurs ()
#  time.sleep (2)
  collecteDonnees ()
  versInfluxDB ()

  print (datetime.datetime.now())
  print ("T eau: " + str(Teau) + "  T air: " + str(Tair) + '  Hygro: ' + str(Hygro) + "  Pression: " + str(Pression) + "  T Elec: " + str (Telec) + " Lux: " + str (Luminosite))
  print ()
  time.sleep (300)

ser.close

