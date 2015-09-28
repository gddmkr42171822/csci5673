'''
Created on Sep 27, 2015

@author: Bob
'''
from Server import Server
from Client import Client
from threading import Thread
import time

def assertion(boolean, testName):
    if boolean:
        print(testName + " PASSED")
    else:
        print(testName + " FAILED")
        
def main():
    testClientConnectionToWithoutLeadershipChangeInCluster()
    testIncorrectClientCommandsToCluster()
    testCorrectClientCommandsToCluster()
    testClientLoop()
    testClientAndServerTimeout()
    testClientLoopWithTimeout()    

def testClientLoopWithTimeout():
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    t1 = Thread(target=s1.electionTimeout)
    t1.start()
    time.sleep(5)
    t2 = Thread(target=s2.electionTimeout)
    t2.start()
    t3 = Thread(target=s3.electionTimeout)
    t3.start()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s2.neighbors)
    
    # Use the command line
    c1.waitForCommands()

def testClientAndServerTimeout():
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    t1 = Thread(target=s1.electionTimeout)
    t1.start()
    time.sleep(5)
    t2 = Thread(target=s2.electionTimeout)
    t2.start()
    t3 = Thread(target=s3.electionTimeout)
    t3.start()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s3.neighbors)
    
    assertion(c1.clusterLeader.uuid == s1.uuid, "Client is connected to the leader.")
    
    # Test queue creation
    label1 = 1
    label2 = 2
    qid1 = c1.clusterLeader.clientCommand("create_Queue", label1)
    qid2 = c1.clusterLeader.clientCommand("create_Queue", label2)
    assertion(len(c1.clusterLeader.stateMachine) == 2, "Client successfully created queue.")
    
    # Test getting qid
    assertion(c1.clusterLeader.clientCommand("get_qid", label1) == qid1, "Client successfully retrieved queue id.")
    assertion(c1.clusterLeader.clientCommand("get_qid", label2) == qid2, "Client successfully retrieved queue id.")
    
    # Test pushing, popping, top, and qsize
    c1.clusterLeader.clientCommand("push", qid1, 5)
    c1.clusterLeader.clientCommand("push", qid1, 10)
    assertion(c1.clusterLeader.clientCommand("qsize", qid1) == 2, "Queue has the right size.")
    assertion(c1.clusterLeader.clientCommand("pop", qid1) == 5, "Client popped the right item off the queue.")
    assertion(c1.clusterLeader.clientCommand("top", qid1) == 10, "Queue top returned the right item off the queue.")
    assertion(c1.clusterLeader.clientCommand("qsize", qid1) == 1, "Queue remains the right size.")
    
    assertion(("create_Queue {0}".format(label1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("create_Queue {0}".format(label2), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("get_qid {0}".format(label1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("get_qid {0}".format(label2), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("push {0} {1}".format(qid1, 5), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("push {0} {1}".format(qid1, 10), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("pop {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("top {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("create_Queue {0}".format(label1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("create_Queue {0}".format(label2), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("get_qid {0}".format(label1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("get_qid {0}".format(label2), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("push {0} {1}".format(qid1, 5), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("push {0} {1}".format(qid1, 10), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("pop {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("top {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(len(s2.stateMachine) == 2, "Follower has the right size state machine.")
    
    # Test the killing of the server and re-election
    c1.clusterLeader.clientCommand("kill")
    time.sleep(5)
    
    assertion(c1.clusterLeader != s1.uuid, "Client is connected to the new leader.")
    assertion(len(c1.clusterLeader.neighbors) == 2, "New leader has the right number of neighbors.")
    
    
    
    
    
def testClientLoop():
    # Establish cluster
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    # Set cluster membership
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    # Create cluster leader
    # Request an election
    s3.requestVotes()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s3.neighbors)
    
    # Use the command line
    c1.waitForCommands()

def testCorrectClientCommandsToCluster():
    # Establish cluster
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    # Set cluster membership
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    # Create cluster leader
    # Request an election
    s3.requestVotes()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s1.neighbors)
    assertion(c1.clusterLeader.uuid == s3.uuid, "Client is connected to the leader.")
    
    # Test queue creation
    label1 = 1
    label2 = 2
    qid1 = c1.clusterLeader.clientCommand("create_Queue", label1)
    qid2 = c1.clusterLeader.clientCommand("create_Queue", label2)
    assertion(len(c1.clusterLeader.stateMachine) == 2, "Client successfully created queue.")
    
    # Test getting qid
    assertion(c1.clusterLeader.clientCommand("get_qid", label1) == qid1, "Client successfully retrieved queue id.")
    assertion(c1.clusterLeader.clientCommand("get_qid", label2) == qid2, "Client successfully retrieved queue id.")
    
    # Test pushing, popping, top, and qsize
    c1.clusterLeader.clientCommand("push", qid1, 5)
    c1.clusterLeader.clientCommand("push", qid1, 10)
    assertion(c1.clusterLeader.clientCommand("qsize", qid1) == 2, "Queue has the right size.")
    assertion(c1.clusterLeader.clientCommand("pop", qid1) == 5, "Client popped the right item off the queue.")
    assertion(c1.clusterLeader.clientCommand("top", qid1) == 10, "Queue top returned the right item off the queue.")
    assertion(c1.clusterLeader.clientCommand("qsize", qid1) == 1, "Queue remains the right size.")
    
    assertion(("create_Queue {0}".format(label1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("create_Queue {0}".format(label2), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("get_qid {0}".format(label1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("get_qid {0}".format(label2), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("push {0} {1}".format(qid1, 5), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    assertion(("push {0} {1}".format(qid1, 10), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("pop {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("top {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in c1.clusterLeader.log, "Leader has the right command in the log.")
    
    assertion(("create_Queue {0}".format(label1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("create_Queue {0}".format(label2), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("get_qid {0}".format(label1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("get_qid {0}".format(label2), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("push {0} {1}".format(qid1, 5), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    assertion(("push {0} {1}".format(qid1, 10), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("pop {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("top {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(("qsize {0}".format(qid1), 1, False, 0) in s2.log, "Follower has the right command in the log.")
    
    assertion(len(s2.stateMachine) == 2, "Follower has the right size state machine.")
    
def testIncorrectClientCommandsToCluster():
    # Establish cluster
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    # Set cluster membership
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    # Create cluster leader
    # Request an election
    s3.requestVotes()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s1.neighbors)
    assertion(c1.clusterLeader.uuid == s3.uuid, "Client is connected to the leader.")
    
    # Test queue creation
    label1 = 1
    label2 = 2
    qid1 = c1.clusterLeader.create_Queue(label1)
    qid2 = c1.clusterLeader.create_Queue(label2)
    assertion(len(c1.clusterLeader.stateMachine) == 2, "Client successfully created queue.")
    
    # Test getting qid
    assertion(c1.clusterLeader.get_qid(label1) == qid1, "Client successfully retrieved queue id.")
    assertion(c1.clusterLeader.get_qid(label2) == qid2, "Client successfully retrieved queue id.")
    
    # Test pushing, popping, top, and qsize
    c1.clusterLeader.push(qid1, 5)
    c1.clusterLeader.push(qid1, 10)
    assertion(c1.clusterLeader.qsize(qid1) == 2, "Queue has the right size.")
    assertion(c1.clusterLeader.pop(qid1) == 5, "Client popped the right item off the queue.")
    assertion(c1.clusterLeader.top(qid1) == 10, "Queue top returned the right item off the queue.")
    assertion(c1.clusterLeader.qsize(qid1) == 1, "Queue remains the right size.")
    

def testClientConnectionToWithoutLeadershipChangeInCluster():
    # Establish cluster
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    # Set cluster membership
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    # Create cluster leader
    # Request an election
    s2.requestVotes()
    
    # Connect the client to the cluster leader through a non-leader
    c1 = Client()
    c1.connectClientToLeader(s1.neighbors)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    c1.connectClientToLeader(s2.neighbors)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    c1.connectClientToLeader(s3.neighbors)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    

if __name__ == '__main__':
    main()