'''
Created on Sep 10, 2015

@author: Bob

Sources
-------
https://pymotw.com/2/socket/udp.html - UDP echo server and client code

Pseudocode
-----------

Part 1: Establish Sever on IP address and port
Create UDP socket
Bind Server to ip address and port

Part 2: Wait for messages and echo them back
Infinite while loop to wait
Receive the data and then resend it
Repeat

Part 3: TODO handle exceptions

'''
import socket

def main():
    #Create the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #Bind the server to localhost and a port between 1024 and 65535
    sock.bind(('', 0))
    print "Bound server to address {0} and port {1}".format(sock.getsockname()[0], sock.getsockname()[1])
    
    #wait for messages to come it
    #receive a message up to 1024 bytes 
    try:
        data, addr = sock.recvfrom(1024)
        print "Received {0} bytes from {1}".format(len(data), addr)
        print "Message received: {0}".format(data)
    
        #send the message back to the client
        if data:
            sent = sock.sendto(data, addr)
            print "Sent {0} bytes back to {1}.".format(sent, addr)
    finally:
        sock.close()
        print "Closed server socket."
        
if __name__ == '__main__':
    main()