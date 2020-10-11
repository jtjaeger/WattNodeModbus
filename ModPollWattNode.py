#!/usr/bin/env python
'''
Pymodbus Asynchronous Client to poll WattNode Modbus
--------------------------------------------------------------------------


'''

import urllib2
import time
import socket
import logging

#---------------------------------------------------------------------------#
# import the various server implementations
#---------------------------------------------------------------------------#
#from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

#---------------------------------------------------------------------------#
# configure the client logging
#---------------------------------------------------------------------------#
LogFile              = "/var/log/ModPollWattNode.log"
WatchdogFile         = "/tmp/ModPollWattNode_Watchdog"

logging.basicConfig(filename=LogFile,format='%(asctime)s %(message)s',level=logging.DEBUG)
log = logging.getLogger()
#log.setLevel(logging.DEBUG) ## logging.ERROR


#---------------------------------------------------------------------------#
# Parameters
#---------------------------------------------------------------------------#

# emoncms
host = "localhost"
port = 50012
#nodeid = 12

# modbus
unitID = [0x0b, 0x0c] # 11=WTG#1, 12=PV
nodeID = [11, 12]
interval = 10    # in seconds

#---------------------------------------------------------------------------#
# WattNode Power Meter Modbus table
#---------------------------------------------------------------------------#

adr_Block01 = 1000
adr_Block02 = 1138

#---------------------------------------------------------------------------#
# Procedures
#---------------------------------------------------------------------------#

# create 8-bit registers
def eightBit(x,y):
	a = (x >> 8) & 0xff
	b = x & 0xff

        c = (y >> 8) & 0xff
        d = y & 0xff

    	return [b, a, d, c]

# poll modbus registers
def pollWattNode(slaveID):

	# Read Modbus Block 1
	result = client.read_holding_registers(adr_Block01, 34, unit=slaveID)
	if result is not None:
		if (result.function_code < 0x80):
			
			# Net Energy, Registers 1000-1001
			reg_ENet = eightBit(result.registers[0], result.registers[1])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[0:3], endian=Endian.Little)
			flt_ENet = decoder.decode_32bit_float()
			#int_ENet = int(10 * decoder.decode_32bit_float())
			logging.debug("EnergyNet: "+str(flt_ENet))
	                
			# Positive Energy, Registers 1002-1003
			reg_EPos = eightBit(result.registers[2], result.registers[3])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[2:5], endian=Endian.Little)
                        flt_EPos = decoder.decode_32bit_float()
			#int_EPos = int(10 * decoder.decode_32bit_float())
                        logging.debug("EnergyPos: "+str(flt_EPos))

			# Active Power Sum, Registers 1008-1009
			reg_PSum = eightBit(result.registers[8], result.registers[9])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[8:11], endian=Endian.Little)
			flt_PSum = decoder.decode_32bit_float()
			#int_PSum = int(round(10*decoder.decode_32bit_float()))
			logging.debug("PwrSum: "+str(flt_PSum))
			
                        # Voltage phase A, Registers 1018-1019
			reg_VoltA = eightBit(result.registers[18], result.registers[19])
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[18:21], endian=Endian.Little)
                        flt_VoltA = decoder.decode_32bit_float()
			#int_VoltA = int(round(10 * decoder.decode_32bit_float()))
                        logging.debug("VoltA: "+str(flt_VoltA))
                        
                        # Voltage phase B, Registers 1020-1021
			reg_VoltB = eightBit(result.registers[20], result.registers[21])
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[20:23], endian=Endian.Little)
                        flt_VoltB = decoder.decode_32bit_float()
			#int_VoltB = int(round(10 * decoder.decode_32bit_float()))
                        logging.debug("VoltB: "+str(flt_VoltB))

                        # Voltage phase C, Registers 1022-1023
			reg_VoltC = eightBit(result.registers[22], result.registers[23])
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[22:25], endian=Endian.Little)
                        flt_VoltC = decoder.decode_32bit_float()
			#int_VoltC = int(round(10 * decoder.decode_32bit_float()))
                        logging.debug("VoltC: "+str(flt_VoltC))
                 
		        # Frequency, Registers 1032-1033
			reg_Freq = eightBit(result.registers[32], result.registers[33])
        	        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[32:35], endian=Endian.Little)
                        flt_F = decoder.decode_32bit_float()
			#int_F = int(round(100 * decoder.decode_32bit_float()))
                        logging.debug("Freq: "+str(flt_F))
                        
        else:
               	logging.error("Modbus result is NONE")


	# Read Modbus Block 02
	result = client.read_holding_registers(adr_Block02, 32, unit=slaveID)
	if result is not None:
		if (result.function_code < 0x080):

                        # Reactive Power Sum, Regiseters 1146-1147 (0-1)
                        reg_Pf = eightBit(result.registers[0], result.registers[1])
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[0:11], endian=Endian.Little)
                        flt_Pf = decoder.decode_32bit_float()
			#int_Pf = int(round(100 * decoder.decode_32bit_float()))
                        logging.debug("Pf: "+str(flt_Pf))

                        # Reactive Power Sum, Regiseters 1146-1147 (08-09)
			reg_QSum = eightBit(result.registers[8], result.registers[9])
                        decoder = BinaryPayloadDecoder.fromRegisters(result.registers[8:11], endian=Endian.Little)
                        flt_QSum = decoder.decode_32bit_float()
			#int_QSum = int(round(10*decoder.decode_32bit_float()))
                        logging.debug("QSum: "+str(flt_QSum))
                       
			# Current Phase A, Register 1162-1163 (24-25)
			reg_IPhA = eightBit(result.registers[24], result.registers[25])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[24:27], endian=Endian.Little)
			flt_IPhA = decoder.decode_32bit_float()
			#int_IPhA = int(round(100 * decoder.decode_32bit_float()))
			logging.debug("IPhA: "+str(flt_IPhA))

			# Read Current Phase B, Register 1164-1165 (26-27)
			reg_IPhB = eightBit(result.registers[26], result.registers[27])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[26:29], endian=Endian.Little)
			flt_IPhB = decoder.decode_32bit_float()
			#int_IPhB = int(round(100 * decoder.decode_32bit_float()))
			logging.debug("IPhB: "+str(flt_IPhB))

			# Current Phase C, Register 1166-1167
			reg_IPhC = eightBit(result.registers[28], result.registers[29])
			decoder = BinaryPayloadDecoder.fromRegisters(result.registers[28:31], endian=Endian.Little)
			flt_IPhC = decoder.decode_32bit_float()
			#int_IPhC = int(round(100 * decoder.decode_32bit_float()))
			logging.debug("IPhC: "+str(flt_IPhC))

        else:
                logging.error("result is NONE")


	#intPayload = [int_ENet,int_PSum,int_QSum,int_VoltA,int_VoltB,int_VoltC,int_IPhA,int_IPhB,int_IPhC,int_F]
	regPayload = reg_ENet + reg_EPos + reg_PSum + reg_QSum + reg_Pf + reg_VoltA + reg_VoltB + reg_VoltC + reg_IPhA + reg_IPhB + reg_IPhC + reg_Freq

	logging.debug(" regPayload: "+str(regPayload))

	return regPayload
	
# Send the frame of data via a socket
def send(frame):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    frame = frame + '\r\n'
    s.send(frame)
    s.close()

#---------------------------------------------------------------------------#
# Main
#---------------------------------------------------------------------------#

logging.debug("Initiating ModbusRTU Interface..")

client = ModbusClient(method='rtu', port='/dev/ttyAMA0', unit=1, baudrate=19200, timeout=1)
if (client.connect()):
        logging.debug(" ..Modbus Connection Successful!")
else:
        logging.debug(" ..Modbus Connection FAILED...")

lastsent = time.time()//interval*interval

# Do forever...
while True:

    # Write time to watchdog file, as a sign of life  
    f3=open(WatchdogFile, "w")
    timestamp = int(time.time())
    f3.write (str(timestamp))
    f3.close()

    # Determine current interval period
    t = time.time()//interval*interval
	
    # Check for 1 interval period since lastsent
    if t >= (lastsent + interval):

        logging.debug(" Polling Registers...")

	# Loop through each Unit ID
	for k in range(0, len(unitID)):

            logging.debug(" k = "+str(k))
	   
	    #list = pollWattNode(unitID(k))
	    list = pollWattNode(unitID[k])
            logging.debug(" LIST: "+str(list))

            # Create a space seperated frame, timestamp nodeid val1 val2 etc
            frame = ' '.join(str(val) for val in [t, nodeID[k]] + list)

            # Update time lastsent
            lastsent = t

            # Print and/or send data
            logging.debug(" Frame:"+frame)

	    try:
                send(frame)
	    except:
                logging.error("FAILED to send data frame via Socket!")		


    # Don't loop too fast
    time.sleep(0.25)




