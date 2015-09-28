'''
Created on Sep 27, 2015

@author: Bob
'''
from Server import Server
from Client import Client

def assertion(boolean, testName):
    if boolean:
        print(testName + " PASSED")
    else:
        print(testName + " FAILED")
        
def main():
    testClientConnectionToWithoutLeadershipChangeInCluster()
    testClientCommandsToCluster()

def testClientCommandsToCluster():
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
    c1.connectClientToLeader(s1)
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
    assertion(c1.clusterLeader.top(qid1) == 10, "Client topped the right item off the queue.")
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
    c1.connectClientToLeader(s1)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    c1.connectClientToLeader(s2)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    c1.connectClientToLeader(s3)
    assertion(c1.clusterLeader.uuid == s2.uuid, "Client is connected to the leader.")
    
    

if __name__ == '__main__':
    main()