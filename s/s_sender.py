import socket
import time
import threading
import sys
import struct

WINDOW_SIZE = 10
TIME_OUT_INTERVAL = 20

R3_ADDRESS = ("10.10.3.2", 4444)
R2_ADDRESS = ("10.10.2.1", 4444)
R1_ADDRESS = ("10.10.1.1", 4444)

current_window = 0
packet_index = 1
finished = False
fin_ack_received = False
packets = []
packet_mutex = threading.Lock()
window_mutex = threading.Lock()

def UDP_RDT_Client(experimentNo, file_name):
    global packet_index
    global current_window
    global finished
    global packets
    global packet_mutex
    global window_mutex

    header = 1
    # Create packets with incresing headers of 2 bytes.
    with open(file_name,"rb") as f:
        while True:
            payload = f.read(996)
            if not payload:
                break
            packets.append(header.to_bytes(4, byteorder='big') + payload)
            header += 1

    # Create socket for sending packets to server.
    UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = threading.Thread(target=UDP_RDT_Listen_Ack, args=(UDPClientSocket, len(packets)))
    t.start()

    if experimentNo=="1":
        UDP_RDT_Sender(UDPClientSocket, R3_ADDRESS)
        
    elif experimentNo == "2":
        t1 = threading.Thread(target=UDP_RDT_Sender, args=(UDPClientSocket, R1_ADDRESS))
        t2 = threading.Thread(target=UDP_RDT_Sender, args=(UDPClientSocket, R2_ADDRESS))
        t3 = threading.Thread(target=UDP_RDT_Sender, args=(UDPClientSocket, R3_ADDRESS))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

    else:
        raise ("Experiment no is invalid!")
    t.join()

def UDP_RDT_Sender(UDPClientSocket, address):
    global packet_index
    global current_window
    global finished
    global packets
    global packet_mutex
    global window_mutex
    global fin_ack_received

    while not finished:
        if current_window>=WINDOW_SIZE:
            continue
        elif packet_index<=len(packets):
            with packet_mutex:
                packet = packets[packet_index-1]
                packet_index += 1
                print("Packet sent:", packet_index)
            # Send the packet
            n_bytes = UDPClientSocket.sendto(packet, address)
            with window_mutex:
                current_window += 1

    fin = 0
    finPacket = fin.to_bytes(4, byteorder='big')

    while not fin_ack_received:
        # Send finish
        UDPClientSocket.sendto(finPacket, address)
        time.sleep(0.5)


def UDP_RDT_Listen_Ack(DSocket, n_packets):
    global packet_index
    global current_window
    global finished
    global packet_mutex
    global window_mutex
    global fin_ack_received

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

    while True: 
        packet, address = DSocket.recvfrom(1024)
        packet = int.from_bytes(packet, byteorder="big")  
        if packet == 0:
            fin_ack_received = True
            break   

if __name__ == "__main__":
    # Create UDPClient and start sending messages.
    UDP_RDT_Client(sys.argv[1], "input1.txt")
