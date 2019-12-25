import socket
import time
import threading
import sys
import struct

WINDOW_SIZE = 10
TIME_OUT_INTERVAL = 20

current_window = 0
packet_index = 1
finished = False

def UDP_RDT_Client(serverIP, serverPort, experimentNo, file_name):
    global packet_index
    global current_window
    global finished

    if experimentNo==1:
        # Create socket for sending packets to server.
        UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverAddressPort = (serverIP, serverPort)

        header = 1
        packets = []
        # Create packets with incresing headers of 2 bytes.
        with open(file_name,"rb") as f:
            while 1:
                payload = f.read(996)
                if not payload:
                    break
                packets.append(header.to_bytes(4, byteorder='big') + payload)
                header += 1

        packet_mutex = threading.Lock()
        window_mutex = threading.Lock()
        t = threading.Thread(target=UDP_RDT_Listen_Ack, args=(UDPClientSocket, len(packets), window_mutex, packet_mutex))
        t.start()

        while not finished:
            if current_window>=WINDOW_SIZE:
                continue
            elif packet_index<=len(packets):
                packet = packets[packet_index-1]
                # Send the packet
                n_bytes = UDPClientSocket.sendto(packet, serverAddressPort)
                print("Packet sent:", packet_index, current_window)
                packet_index += 1
                with window_mutex:
                    current_window += 1
            
        # Send finish
        fin = 0
        finPacket = fin.to_bytes(4, byteorder='big')
        UDPClientSocket.sendto(finPacket, serverAddressPort)
        
    elif experimentNo == 2:
        pass
    else:
        raise ("Experiment no is invalid!")

    t.join()

def UDP_RDT_Listen_Ack(DSocket, n_packets, window_mutex, packet_mutex):
    global packet_index
    global current_window
    global finished

    expected_ack = 2
    timer_running = False
    bad_ack_time = 99999999999999999
    while True:
        d_ack = int.from_bytes(DSocket.recv(1024), byteorder="big")
        if d_ack == n_packets + 1:
            finished = True
            break
        elif d_ack >= expected_ack:
            with window_mutex:
                current_window -= d_ack - expected_ack + 1
                expected_ack = d_ack + 1
                timer_running = False
            if d_ack > packet_index:
                with packet_mutex:
                    packet_index = d_ack
        else:
            print(int(round(time.time() * 1000)) - bad_ack_time)
            if not timer_running:
                bad_ack_time = int(round(time.time() * 1000))
                timer_running = True
            elif int(round(time.time() * 1000)) - bad_ack_time > TIME_OUT_INTERVAL:
                print("CHANGING VARIABLES")
                with packet_mutex:
                    packet_index = d_ack
                with window_mutex:
                    current_window = 0
                    expected_ack = d_ack + 1
                print("PACKET INDEX:", packet_index)
                print("EXPECTED ACK:", expected_ack)
                print("CURRENT WINDOW:", current_window)
                timer_running = False

if __name__ == "__main__":
    # Create UDPClient and start sending messages.
    UDP_RDT_Client("10.10.3.2", 4444, 1, "input1.txt")
