'''
Created on Sep 10, 2015

@author: Bob

Sources
-------
https://pymotw.com/2/socket/udp.html - UDP echo server and client code

Pseudocode
-----------

Part 1: Establish Client on machine

Figure out ip of server and its port
Create UDP socket

Part 2: Wait for messages and echo them back
Infinite while loop to wait
Receive the data and then resend it
Repeat

Part 3: Record local clock times when sending and receiving (maybe output them to a file?)

Part 4: TODO handle exceptions


'''
import socket

def main():
    serverIP = '0.0.0.0'
    serverPort = 56513
    
    #create the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #message to be sent to server
    message = 'Hello World!'
    
    try: 
        #send the message
        print "Sending {0} to {1} on port {2}.".format(message, serverIP, serverPort)
        sock.sendto(message, (serverIP, serverPort))
        
        #wait for echo from server
        print "Waiting for echo from server."
        data, serverAddr = sock.recvfrom(1024)
        print "Received {0} bytes from {1}".format(len(data), serverAddr)
        print "Message received: {0}".format(data)
    finally:
        sock.close()
        print "Closed client socket."
        
    
    

if __name__ == '__main__':
    main()