import socket
import time
import threading
import sys
import struct

R3_ADDRESS = ("10.10.3.2", 4444)
R2_ADDRESS = ("10.10.2.1", 4444)
R1_ADDRESS = ("10.10.1.2", 4444)
WINDOW_SIZES = {R1_ADDRESS:10, R2_ADDRESS:10, R3_ADDRESS:20}
TIME_OUT_INTERVAL = 2000

packets_flow = {R1_ADDRESS:[], R2_ADDRESS:[], R3_ADDRESS:[]}
n_packets_flow = {R1_ADDRESS:0, R2_ADDRESS:0, R3_ADDRESS:0}
packet_index = 1
finished = False
fin_ack_received = False
packets = []
packet_mutex = threading.Lock()
n_packet_mutex = threading.Lock()

def UDP_RDT_Client(experimentNo, file_name):
    global packet_index
    global n_packets_flow
    global finished
    global packets
    global packet_mutex
    global n_packet_mutex

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
    global n_packets_flow
    global finished
    global packets
    global packet_mutex
    global fin_ack_received
    global n_packet_mutex
    global packets_flow

    while not finished:
        if n_packets_flow[address]>=WINDOW_SIZES[address]:
            continue
        elif packet_index<=len(packets):
            with packet_mutex:
                packet = packets[packet_index-1]
                print("Packet sent to:", packet_index, address)
                packet_index += 1
            # Send the packet
            UDPClientSocket.sendto(packet, address)
            with n_packet_mutex:
                n_packets_flow[address] += 1
                packets_flow[address].append(packet_index)

    fin = 0
    finPacket = fin.to_bytes(4, byteorder='big')

    while not fin_ack_received:
        # Send finish
        UDPClientSocket.sendto(finPacket, address)
        time.sleep(0.5)


def UDP_RDT_Listen_Ack(DSocket, n_packets):
    global packet_index
    global n_packets_flow
    global finished
    global packet_mutex
    global n_packet_mutex
    global fin_ack_received
    global packets_flow

    expected_ack = 2
    successful_sent = {R1_ADDRESS:0, R2_ADDRESS:0, R3_ADDRESS:0}

    while True:
        d_ack = int.from_bytes(DSocket.recv(1024), byteorder="big")

        if d_ack == n_packets + 1:
            finished = True
            break
        elif d_ack >= expected_ack:
            for address in packets_flow:
                sent_packet_indices = packets_flow[address]
                for sent_packet_index in sent_packet_indices:
                    if (sent_packet_index < d_ack):
                        successful_sent[address] += 1

            with n_packet_mutex:
                for address in n_packets_flow:
                    n_packets_flow[address] -= successful_sent[address]
                    packets_flow[address] = []
            expected_ack = d_ack + 1
        else:
            with n_packet_mutex:
                for address in n_packets_flow:
                    n_packets_flow[address] = 0
                    packets_flow[address] = []
            expected_ack = d_ack + 1
        with packet_mutex:
            packet_index = d_ack


    while True: 
        packet, address = DSocket.recvfrom(1024)
        packet = int.from_bytes(packet, byteorder="big")  
        if packet == 0:
            fin_ack_received = True
            break   

if __name__ == "__main__":
    # Create UDPClient and start sending messages.
    UDP_RDT_Client(sys.argv[1], "input1.txt")
