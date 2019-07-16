from time import sleep

class VITA_PRINTER():
    def __init__(self):
        pass
    #send G1 X Y Z F code to printer. Send default 0 for inputs
    def printerMove(self, controller,x,y,z,f):
        ser = controller.ser
        #to change in future
        if abs(x) <= 100 or abs(y) <= 100 or abs(z) <= 10:
            cmdRelative = "G91 \r\n"
            cmdMove = "G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(f) + "\r\n"
            #remember the b
            ser.write(self.strToBin(cmdRelative))
            self.printerCheckOk(controller)
            sleep(0.2)
            ser.write(self.strToBin(cmdMove))
            self.printerCheckOk(controller)
            print("1")
            sleep((max([abs(x), abs(y), abs(z)])*60*1/f*1.2))
        else:
            print("sorry Jim, i cannot do that")
            controller.terminate()

    #check for an okay
    def printerCheckOk(self, controller):
        ser = controller.ser
        if ser.is_open:
            response = ser.readline()
            print(response)
            if response == b"ok\n":
                return True
            print("printer error. things not okay! t('_'t)")
        else:
            print("serial port /dev/ttyUSB0 not open")
        controller.terminate()
        
        #convert ot ascii bytes
    def strToBin(self,command):
        return bytes(command, encoding = "ascii")

        
