#!/usr/bin/env python3

'''

    Character size is 8 bits with one stop bit and hardware flow control.

"python -m serial.tools.list_ports" will list all serial ports.
'''


import serial
import sys
#  from __builtin__ import None


if 'darwin' in sys.platform:
    portIdentifier = "/dev/cu.usbserial-AB0JNVRD"
elif 'linux' in sys.platform:
    portIdentifier = "/dev/ttyUSB0"
else:
    portIdentifier = Input("Unknown platform.  Enter serial device path:")
    
serialPortBaud = 9600 

diskBlockSize = 512         # Defined by UCSD Pascal
diskBlockCount = 2464       # Blocks in an "optimized" volume

diskDirBlock = 2            # Block number containing start of UCSD directory
diskDirLengthOffset = 2     # Byte offset of directory length byte
diskDirCount = {6, 10}      # Blocks in a UCSD volume directory

cleol = "\033[K"            #  Clear to end of line ANSI escape sequence


def main(argv=None):

    try:
        port = serial.Serial(portIdentifier, serialPortBaud, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, 
                             stopbits=serial.STOPBITS_ONE, rtscts=True, exclusive=True)

        
    except Exception as e:
        print("Could not open {0}:  {1}".format(portIdentifier, e))
        return
    
    while True:
        while True:
            try:
                # We want to make sure that there is no buffered up garbage on the serial port, but
                # reset_input_buffer doesn't seem to be doing the job, and 
                # https://github.com/pyserial/pyserial/issues/344 implies that it can't.
                # Work around this by discarding input characters until there are none for a couple
                # of seconds.
                while port.in_waiting > 0:
                    print("Discarding buffered serial data...")
                    port.read(port.in_waiting)
                    time.sleep(4)
                port.reset_input_buffer()      #  Do it anyway, even though it may be a no-op
                filename = input("Enter filename (empty to quit):")
                if (not len(filename)):
                    return
                f = open(filename, "wb")
                break
        
            except Exception as e:
                 print("Could not open {0}:  {1}".format(filename, e))
       
        try:
            for blockNumber in range(diskBlockCount):
                block = port.read(diskBlockSize)
                f.write(block)
                print("Block {0:04d}:  {1}...".format(blockNumber, "".join("{:02x}".format(block[i]) for i in range(32)), cleol))    

            # Paranoid check to make sure we didn't pick up any extra bytes at the start of the transfer.
            if blockNumber == diskDirBlock and block[diskDirLengOffset] not in diskDirCount:
               raise("Illegal UCSD directory size.")
            
        except Exception as e:
                print("Error:  {0}".format(e))
                print("Transfer aborted.")

        finally:    
            f.close()
            print("Transfer of {0} complete.".format(filename))


if __name__ == "__main__":
    sys.exit(main())
