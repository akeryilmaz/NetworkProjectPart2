# ROUTER IMPLEMENTATION FOR R3 #
import queue
import socket
import threading

def UDPServer(localIP, localPort, packetQueue_DS, packetQueue_SD):
    # Create UDP Server socket and bind local IP & port to it.
    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP Server on IP {} is ready.".format(localIP))
    while True:
        # Listen for incoming packets from s.
        messageFromS, address = UDPServerSocket.recvfrom(1024)
        # Put the packet into queue for sender thread to send these packets.
        packetQueue_SD.put(messageFromS)
        # From the queue, get the feedback packet coming from d.
        messageFromD = packetQueue_DS.get()
        # Send the feedback packet back to s
        UDPServerSocket.sendto(messageFromD, address)


def UDPClient(remoteIP, remotePort, packetQueue_DS, packetQueue_SD):
    # Create UDP Client socket
    UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    remoteIPPort = (remoteIP, remotePort)
    while True:
        # Get messages from packetQueue_SD one by one and send it to remoteIP, remotePort.
        messageFromS = packetQueue_SD.get()
        UDPClientSocket.sendto(messageFromS, remoteIPPort)
        # Receive the feedback packet from d.
        messageFromD = UDPClientSocket.recv(1024)
        # Put it in the queue.
        packetQueue_DS.put(messageFromD)

if __name__ == "__main__":
    destinations = {'s' : "10.10.3.1", 'd': "10.10.7.1"}
    sources = {'s': "10.10.3.2", 'd': "10.10.7.2"}

    # There will be 1 server thread running
    # in order to receive the packets sent from s
    # and send response packets back to s.

    # There will also be 1 client thread which sends
    # packets received from server thread to d
    # and receive response packets.

    # This queue stores packets which are sent by s to d. (Shared between packet receiver from s (server thread) and packet sender to d (client thread))
    s_to_d_queue = queue.Queue()
    # This queue stores packets which are sent by d to s. (Shared between packet receiver from d (client thread) and packet sender to s (server thread))
    d_to_s_queue = queue.Queue()

    serverThread = threading.Thread(target=UDPServer, args=(sources['s'], 4444, d_to_s_queue, s_to_d_queue))
    clientThread = threading.Thread(target=UDPClient, args=(destinations['d'], 4444, d_to_s_queue, s_to_d_queue))
    serverThread.start()
    clientThread.start()
    serverThread.join()
    clientThread.join()
    
