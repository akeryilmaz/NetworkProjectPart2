import socket
import time
import threading
import sys

received_packets = {}
mutex = threading.Lock()
key_max = -1
ack = 1
finished = False
started = False
r1_count = 0
r2_count = 0
r3_count = 0
socket_dict = {}

def UDP_RDT_Server(localIP, localPort):
    global key_max
    global received_packets
    global ack
    global finished
    global socket_dict
    global started

    # Create UDP Server socket and bind local IP & port to it.
    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP_RDT_Server Server on IP {} is ready.".format(localIP))

    while not finished:
        # Listen for incoming packets.
        packet, address = UDPServerSocket.recvfrom(1024)
        socket_dict[UDPServerSocket] = address
        started = True
        header = packet[:4]
        current_key = int.from_bytes(header, byteorder="big")
        # key 0 means thread is finished
        if current_key == 0:
            UDPServerSocket.sendto(current_key.to_bytes(4, byteorder='big'), address)
            finished = True
        else:
            with mutex:
                received_packets[current_key] = packet[4:]

def ACKHandler():
    print("Ack handler thread created.")
    while not finished:
        last_consec = gap_check()
        with mutex:
            for k in socket_dict:
                k.sendto(last_consec.to_bytes(4, byteorder='big'), socket_dict[k])
                print("sent ACK:", last_consec)
            time.sleep(0.015)

def gap_check():
    global received_packets
    last_consec = 1
    mylist = list(received_packets.keys())
    mylist.sort()
    for mykey in mylist:
        if mykey == last_consec:
            last_consec += 1
        else:
            break
    return last_consec

if __name__ == "__main__":
    # Start listening for messages coming from r3 as a UDPServer.
    experiment_no = sys.argv[1]
    if experiment_no == "1":
        t1 = threading.Thread(target=UDP_RDT_Server, args=("10.10.7.1", 4444))
        t2 = threading.Thread(target=ACKHandler)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    elif experiment_no == "2":
        t1 = threading.Thread(target=UDP_RDT_Server, args=("10.10.7.1", 4444))
        t2 = threading.Thread(target=UDP_RDT_Server, args=("10.10.5.2", 4444))
        t3 = threading.Thread(target=UDP_RDT_Server, args=("10.10.4.2", 4444))
        t4 = threading.Thread(target=ACKHandler)
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
    else:
        print("INVALID EXP NO")
        sys.exit()
    with open("output"+experiment_no+".txt", "wb") as f: 
        for key in range(1, key_max+1):
            f.write(received_packets[key])
