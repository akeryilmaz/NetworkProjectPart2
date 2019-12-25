import socket
import time
import threading
import sys
import struct

WINDOW_SIZE = 30
TIME_OUT_INTERVAL = 40

def UDP_RDT_Client(serverIP, serverPort, experimentNo, file_name):
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

        current_window = 0
        packet_index = 1
        packet_mutex = threading.Lock()
        window_mutex = threading.Lock()
        t = threading.Thread(target=UDP_RDT_Listen_Ack, args=(UDPClientSocket, current_window, packet_index, window_mutex, packet_mutex))
        t.start()

        while True:
            if current_window>=WINDOW_SIZE:
                continue
            else:
                packet = packets[packet_index-1]
                # Send the packet
                n_bytes = UDPClientSocket.sendto(packet, serverAddressPort)
                print("Packet sent:", packet_index)
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

def UDP_RDT_Listen_Ack(DSocket, current_window, packet_index, window_mutex, packet_mutex):
    expected_ack = 1
    timer_running = False
    while True:
        d_ack = int.from_bytes(DSocket.recv(1024), byteorder="big")
        print("Ack received: ", d_ack)
        if d_ack >= expected_ack:
            with window_mutex:
                current_window -= d_ack - expected_ack + 1
                expected_ack = d_ack + 1
                timer_running = False
        else:
            if not timer_running:
                bad_ack_time = int(round(time.time() * 1000))
                timer_running = True
            elif int(round(time.time() * 1000)) - bad_ack_time > TIME_OUT_INTERVAL:
                with packet_mutex:
                    packet_index = d_ack
                with window_mutex:
                    current_window -= d_ack - expected_ack + 1
                    expected_ack = d_ack + 1


if __name__ == "__main__":
    # Create UDPClient and start sending messages.
    UDP_RDT_Client("10.10.3.2", 4444, 1, "input1.txt")
