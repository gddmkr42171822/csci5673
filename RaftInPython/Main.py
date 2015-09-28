'''
Created on Sep 25, 2015

@author: Bob
'''
from Server import Server
from Client import Client
from threading import Thread
import time

def main():
    
    # Establish the server cluster
    s1 = Server()
    s2 = Server()
    s3 = Server()
    s4 = Server()
    s5 = Server()
    
    s1.setNeighbors([s2, s3, s4, s5])
    s2.setNeighbors([s1, s3, s4, s5])
    s3.setNeighbors([s2, s1, s4, s5])
    s4.setNeighbors([s2, s3, s1, s5])
    s5.setNeighbors([s2, s3, s4, s1])
    
    t1 = Thread(target=s1.electionTimeout)
    t1.start()
    time.sleep(5)
    t2 = Thread(target=s2.electionTimeout)
    t2.start()
    t3 = Thread(target=s3.electionTimeout)
    t3.start()
    t4 = Thread(target=s4.electionTimeout)
    t4.start()
    t5 = Thread(target=s5.electionTimeout)
    t5.start()
    
    # Connect the client to the cluster leader
    c1 = Client()
    c1.connectClientToLeader(s2.neighbors)
    
    # Use the command line
    c1.waitForCommands()

if __name__ == '__main__':
    main()