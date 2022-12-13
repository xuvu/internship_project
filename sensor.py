import serial

class device:
  
  def __init__(self, port, brate):
    self.port = port
    self.brate = brate
    self.serialPort = serial.Serial(port = self.port, baudrate=self.brate,
                           bytesize=8, stopbits=serial.STOPBITS_ONE)

  def connectAgain(self):
    self.serialPort.close()
    self.serialPort = serial.Serial(port = self.port, baudrate=self.brate,
                           bytesize=8, stopbits=serial.STOPBITS_ONE)

  def getHeightWeightTemp(self):

    # get the weight and heiht from sensor
    serialString = "" # Used to hold data coming over UART

    height = None
    weight = None
    temp = None
    
    if(self.serialPort.isOpen()):
      while(1):

          # Wait until there is data waiting in the serial buffer
          if(self.serialPort.in_waiting > 0):

              # Read data out of the buffer until a carraige return / new line is found
              serialString = self.serialPort.readline()

              # Print the contents of the serial data
              allString = serialString.decode('Ascii')
              allString = allString.replace('\n','')
              allString = allString.replace('\r','')
              allString = allString.replace(' ','')
              #print(allString)
              
              weightPos = allString.find("W")
              heightPos = allString.find("H")
              tempPos = allString.find("T")

              if weightPos != -1 and heightPos != -1:
                weight = allString[weightPos+2:heightPos]
                height = allString[heightPos+2:]

              if tempPos != -1:
                temp = allString[tempPos+2:]

              if weight != None  and height != None  and temp != None :
                return height,weight,temp
  
  def __del__(self):
    self.serialPort.close()