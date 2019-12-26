import socket
import time
import threading
import sys
import struct

R3_ADDRESS = ("10.10.3.2", 4444)
R2_ADDRESS = ("10.10.2.1", 4444)
R1_ADDRESS = ("10.10.1.2", 4444)
WINDOW_SIZES = {R1_ADDRESS:10, R2_ADDRESS:10, R3_ADDRESS:25}
LINK_FAILURE_TIMEOUT = 5

def UDP_RDT_Sender(UDPClientSocket, address):
    global packet_index
    global n_packets_flow
    global finished
    global packets
    global packet_mutex
    global fin_ack_received
    global n_packet_mutex
    global packets_flow
    global fin_timeout

    while not finished:
        if n_packets_flow[address]>=WINDOW_SIZES[address]:
            continue
        elif packet_index<=len(packets):
            with packet_mutex:
                packet = packets[packet_index-1]
                #print("Packet sent to:", packet_index, address)
                packet_index += 1
            # Send the packet
            UDPClientSocket.sendto(packet, address)
            with n_packet_mutex:
                n_packets_flow[address] += 1
                packets_flow[address].append(packet_index)

    fin = 0
    finPacket = fin.to_bytes(4, byteorder='big')
    fin_count = 0
    while not fin_ack_received and fin_count < 100:
        # Send finish
        UDPClientSocket.sendto(finPacket, address)
        fin_count += 1
        time.sleep(0.05)
    fin_timeout = True


def UDP_RDT_Listen_Ack(DSocket, n_packets):
    global packet_index
    global n_packets_flow
    global finished
    global packet_mutex
    global n_packet_mutex
    global fin_ack_received
    global packets_flow
    global fin_timeout

    expected_ack = 2
    prev_ack = 0
    dup_count = 0
    last_ack_received = {R1_ADDRESS:time.time(), R2_ADDRESS:time.time(), R3_ADDRESS:time.time()}
    down_flag = {R1_ADDRESS:False, R2_ADDRESS:False}

    while True:
        packet, address = DSocket.recvfrom(1024)
        d_ack = int.from_bytes(packet, byteorder="big")
        last_ack_received[address] = time.time()

        for address in down_flag:
            if down_flag[address]:
                continue
            if time.time() - last_ack_received[address] > LINK_FAILURE_TIMEOUT:
                down_flag[address] = True
                WINDOW_SIZES[address] = 0
                print(address[0], "is DOWN!!!11!!!!11!")

        if d_ack == n_packets + 1:
            finished = True
            break
        elif d_ack == prev_ack:
            dup_count += 1
            if dup_count >= 3:
                print("dup ack")
                with n_packet_mutex:
                    for address in n_packets_flow:
                        n_packets_flow[address] = 0
                        packets_flow[address] = []
                expected_ack = d_ack + 1
                with packet_mutex:
                    packet_index = d_ack
                dup_count=0
        elif d_ack >= expected_ack:
            print("good ack:", expected_ack, d_ack)
            max_sent_packet = 0
            with n_packet_mutex:
                for address in packets_flow:
                    sent_packet_indices = packets_flow[address]
                    for i, sent_packet_index in enumerate(sent_packet_indices):
                        if (sent_packet_index < d_ack):
                            expected_ack += 1
                            n_packets_flow[address] -= 1
                            del packets_flow[address][i]
            dup_count = 0
       
        prev_ack = d_ack

    while not fin_timeout: 
        packet, address = DSocket.recvfrom(1024)
        packet = int.from_bytes(packet, byteorder="big")  
        if packet == 0:
            fin_ack_received = True
            break   

if __name__ == "__main__":

    experimentNo = sys.argv[1]
    packets = []
    header = 1
    # Create packets with incresing headers of 2 bytes.
    with open("input1.txt","rb") as f:
        while True:
            payload = f.read(996)
            if not payload:
                break
            packets.append(header.to_bytes(4, byteorder='big') + payload)
            header += 1

    # Create socket for sending packets to server.
    UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    elapsed_times = []
    for i in range(int(sys.argv[2])):
        print("Experiment %d starting" %(i))
        #Fix environment variables
        packets_flow = {R1_ADDRESS:[], R2_ADDRESS:[], R3_ADDRESS:[]}
        n_packets_flow = {R1_ADDRESS:0, R2_ADDRESS:0, R3_ADDRESS:0}
        packet_index = 1
        finished = False
        fin_ack_received = False
        packet_mutex = threading.Lock()
        n_packet_mutex = threading.Lock()
        fin_timeout = False

        start = time.time()

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

        end = time.time()
        elapsed_times.append(end-start)
        print("Experiment %d is finished in %f" %( i, end-start))

        time.sleep(5)

    with open(sys.argv[3],"w") as f:
         for elapsed_time in elapsed_times:
             f.write(str(elapsed_time) + "\n")
