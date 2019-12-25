import socket
import time
import threading

def UDP_RDT_Server(localIP, localPort, experimentNo, file_name):

    if experimentNo==1:
        # Create UDP Server socket and bind local IP & port to it.
        UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPServerSocket.bind((localIP, localPort))
        print("UDP_RDT_Server Server on IP {} is ready.".format(localIP))

        received_packets = {}
        key_max = -1
        #ack is the header of the packet expected.
        ack = 1
        timer_running = False

        while True:
            # Listen for incoming packets.
            try:
                packet, address = UDPServerSocket.recvfrom(1024)
                UDPServerSocket.settimeout(0.3)
            except socket.timeout:
                UDPServerSocket.sendto(ack.to_bytes(4, byteorder='big'), address)
                print("Timeout, sent ACK:", ack)
            header = packet[:4]
            current_key = int.from_bytes(header, byteorder="big")  
            
            # key 0 means thread is finished
            if current_key == 0:
                break
            # Not expected packet, reject
            elif current_key != ack:
                UDPServerSocket.sendto(ack.to_bytes(4, byteorder='big'), address)
                print("Unexpected, sent ACK:", ack)
                

            # Expected packet, accept
            else:
                ack += 1
                payload = packet[4:] 
                received_packets[current_key] = payload 
                if current_key > key_max:
                    key_max = current_key
                UDPServerSocket.sendto(ack.to_bytes(4, byteorder='big'), address)
                print("Sent ACK:", ack)

        with open(file_name,"wb") as f: 
            for key in range(1, key_max+1):
                f.write(received_packets[key])


    elif experimentNo==2:
        pass
    else:
        raise ("Experiment no is invalid!")

if __name__ == "__main__":
    # Start listening for messages coming from r3 as a UDPServer.
    UDP_RDT_Server("10.10.7.1", 4444, 1, "output1.txt")
