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
import datetime

def main():
    
    #Declare empty strings for storing the time a message is sent and received
    timeReceived = ""
    timeSent = ""
    
    sendTimes = []
    receiveTimes = []
    
    #Create the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    #Bind the server to localhost and a port between 1024 and 65535
    sock.bind(('', 0))
    print "Bound server to address {0} and port {1}".format(socket.gethostbyname(socket.gethostname()), sock.getsockname()[1])
    
    try:
        
        #Repeat the send and receive five times
        for i in range(0, 5):
            #wait for messages to come it
            #receive a message up to 1024 bytes 
            data, addr = sock.recvfrom(1024)
            timeReceived = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
            print "Server received message at time: " + timeReceived
            print "Received {0} bytes from {1}".format(len(data), addr)
            print "Message received: {0}".format(data)
        
            #send the message back to the client
            if data:
                sent = sock.sendto(data, addr)
                timeSent = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
                print "Server sent message at time: " + timeSent
                print "Sent {0} bytes back to {1}.".format(sent, addr)
            
            sendTimes.append(timeSent)
            receiveTimes.append(timeReceived)
            
    finally:
        sock.close()
        print "Closed server socket."
    
    outputFilePath = "server_times_same_machine_without_print.txt"
    print "Writing times to the file: " + outputFilePath    
    with open(outputFilePath, "w") as f:
        f.write("Scenario: Client and Server are the same machine.\n")
        for time in sendTimes:
            f.write("Send time: " + time + "\n")
        for time in receiveTimes:
            f.write("Receive time: " + time + "\n")
        
if __name__ == '__main__':
    main()