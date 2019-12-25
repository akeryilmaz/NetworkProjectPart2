import socket
import time
import threading
import sys
import struct


def UDP_RDT_Client(serverIP, serverPort, experimentNo, file_name):
    if experimentNo==1:

        header = 0
        packets = []
        # Create packets with incresing headers of 2 bytes.
        with open(file_name,"rb") as f:
            while 1:
                payload = f.read(997)
                if not payload:
                    break
                packets.append(header.to_bytes(3, byteorder='big') + payload)
                header += 1

        serverAddressPort = (serverIP, serverPort)
        # Create socket for sending packets to server.
        UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packetsSent = 0
        for packet in packets:
            # Send the packet
            n_bytes = UDPClientSocket.sendto(packet, serverAddressPort)
            print(n_bytes)
            packetsSent += 1
            
        # Send finish
        number = -1
        finPacket = number.to_bytes(3, byteorder='big')
        UDPClientSocket.sendto(finPacket, serverAddressPort)
        
    elif experimentNo == 2:
        pass
    else:
        raise ("Experiment no is invalid!")

if __name__ == "__main__":
    # Create UDPClient and start sending messages.
    UDP_RDT_Client("10.10.3.2", 4444, 1, "input1.txt")
