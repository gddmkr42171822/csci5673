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
Receive the data and then resend it
End the server program and close the socket

Part 3: Record local clock times when sending and receiving (maybe output them to a file?)

Part 4: TODO handle exceptions


'''
import socket
import datetime

def main():
    
    #Declare empty strings for storing the time a message is sent and received
    timeReceived = ""
    timeSent = ""
    
    sendTimes = []
    receiveTimes = []
    
    serverIP = '128.138.201.67'
    serverPort = 46805
    #message to be sent to server
    message = 'Hello World!'
    
    #create the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        
        #Repeat the send and receive five times
        for i in range(0, 5):
            #send the message
            print "Sending {0} to {1} on port {2}.".format(message, serverIP, serverPort)
            sock.sendto(message, (serverIP, serverPort))
            timeSent = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
            print "Client send message at time: " + timeSent
            
            #wait for echo from server
            print "Waiting for echo from server."
            data, serverAddr = sock.recvfrom(1024)
            timeReceived = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
            print "Client received message at time: " + timeReceived
            print "Received {0} bytes from {1}".format(len(data), serverAddr)
            print "Message received: {0}".format(data)
            
            #Keep a list of the times a message is sent an received
            sendTimes.append(timeSent)
            receiveTimes.append(timeReceived)
        
    finally:
        sock.close()
        print "Closed client socket."
        
    outputFilePath = "client_times_diff_wan.txt"
    print "Writing times to file: " + outputFilePath
    with open(outputFilePath, "w") as f:
        f.write("Scenario: Client and Server are on different machines accross WAN.\n")
        for time in sendTimes:
            f.write("Send time: " + time + "\n")
        for time in receiveTimes:
            f.write("Receive time: " + time + "\n")
    
    

if __name__ == '__main__':
    main()