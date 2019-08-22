#Joulie-16 Ethernet Communication example
# The Joulie-16 uses UDP MCAST to trasmit all it's values thus it should be used in it's own network to avoid flooding a normal network with loads of data
# Also it is completely un-encrypted
import socket
import crcmod
import os
import time

crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0x0000, xorOut=0x0000)                           # CRC Setup for Joulie-16

ANY = "0.0.0.0" 
MCAST_ADDR = "239.255.73.100"
MCAST_PORT = 1500
MCAST_TTL = 2
BMS_LIST = []


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Allow multiple sockets to use the same PORT number
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

# Bind to the port that we know will receive multicast data
sock.bind((ANY,MCAST_PORT))

# Tell the kernel that we are a multicast socket
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MCAST_TTL)

# Tell the kernel that we want to add ourselves to a multicast group
# The address for the multicast group is the third param
status = sock.setsockopt(socket.IPPROTO_IP,
socket.IP_ADD_MEMBERSHIP,
socket.inet_aton(MCAST_ADDR) + socket.inet_aton(ANY));

# setblocking(0) is equiv to settimeout(0.0) which means we poll the socket.
# But this will raise an error if recv() or send() can't immediately find or send data. 
sock.setblocking(1)
sock.settimeout(1)
count = 0
#try:
#    sock.sendto("928,0,1,TRUE,8182", (MCAST_ADDR, MCAST_PORT))
#except:
#    print "failed"
#    pass
while 1:
    try:
        data, addr = sock.recvfrom(1024)
    except socket.error as e:
        pass
    else:
        if data.split(",")[2] == '100':                                                                 # Check if the Message is a valid BMS status
            count += 1                                                                                  # Increment Message counter
            now = time.strftime("%d.%m.%Y-%H:%M:%S", time.localtime(time.time()))                       # Get current system time
            os.system('clear')                                                                          # Clear terminal
            print "MSG No.: ", count
            print "BMS No.: ", data.split(",")[1]
            f = open("BMS"+data.split(",")[1], "a+")                                                    # Open/create Logfile for each BMS
            f.write(str(now)+','+data+'\r\n')                                                           # Write complete message to logfile
            f.close()                                                                                   # Close the logfile
            if data.split(",")[1] not in BMS_LIST:                                                      # Check if current message is from a new BMS
                BMS_LIST.append(data.split(",")[1])
                sock.sendto(data.split(",")[1]+",0,1,TRUE,"+crc16(data.split(",")[1]+",0,1,TRUE,"))     # Tell the new BMS to turn on the output Relay
            print "Found BMS: ", BMS_LIST
            for i in range(1,1,16):                                                                     # Print all cell voltages
                print "Cell ",i,": ", data.split(",")[i+2], "V"
            print "Block Voltage: ", data.split(",")[-8], "V"                                           # Print current block voltage
            print "Balancer Status: ", data.split(",")[-5]
            print "Relay Active: ", data.split(",")[-2]
            print "CRC Valid: ", int(data.split(",")[-1], 16) == crc16(data[:-4])                       # Show if CRC's match
            print ""                                                                                    # Empty line for cleanliness
