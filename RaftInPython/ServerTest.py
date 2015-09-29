'''
Created on Sep 25, 2015

@author: Bob
'''
from Server import Server
from Server import ServerState
from threading import Thread
import time

def assertion(boolean, testName):
    if boolean:
        print(testName + " PASSED")
    else:
        print(testName + " FAILED")
        
def main():
    
    testInitialServerState()
    testSingleServerBecomesLeaderVoteRequest
    testSingleServerDoesNotReceiveMajorityVotesShouldNotBecomeLeader()
    testLeaderStateMachineLogReplication()
    testElectionTimeout()
    
def testElectionTimeout():
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
    
    # Add to the leaders log a command no none else has
    s1.clusterLeader.log.append(("test", 1, False, 0))
    
    # Add a state machine no one else has
    s1.clusterLeader.stateMachine[1] = "test"

    time.sleep(5)
    assertion(s1.state == ServerState.leader, "Server should be the leader.")
    assertion(s2.state == ServerState.follower, "Server should be the follower.")
    assertion(s3.state == ServerState.follower, "Server should be the follower.")
    
    assertion(len(s1.clusterLeader.log) == 2, "Server has the right size log.")
    assertion(s1.log == s2.log, "Server has the right log.")
    assertion(s3.log == s2.log, "Server has the right log.")
    assertion(s2.log == s3.log, "Server has the right log.")
    
    assertion(len(s1.stateMachine) == 1, "Server has the right size state machine.")
    assertion(s1.stateMachine[1] == s2.stateMachine[1], "Server has the right state machine")
    
    

def testInitialServerState():
    s = Server()
    assertion(s.state == ServerState.follower, "Server should start in the follower state.")

def testSingleServerBecomesLeaderVoteRequest():
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    assertion(len(s1.neighbors) - 1 == 2, "Server should have the right number of neighbors.")
    
    # Request an election
    s1.requestVotes()
    
    assertion(s1.votesReceived == 3, "Server have received the right number of votes.")
    assertion(s1.state == ServerState.leader, "Server should have been elected the leader.")
    assertion(s2.voted == True, "Server should have voted.")
    assertion(s3.voted == True, "Server should have voted.")
    assertion(s1.voted == True, "Server should have voted for itself.")
    assertion(s1.log[0][1] == 0, "Server has the right term in the log.")

def testSingleServerDoesNotReceiveMajorityVotesShouldNotBecomeLeader():
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    s2.voted = True
    s3.voted = True
    
    # Request an election
    s1.requestVotes()
    
    assertion(s1.state == ServerState.candidate, "Server should remain candidate.")
    assertion(s1.votesReceived == 1, "Server should have the correct number of votes.")
    
def testLeaderStateMachineLogReplication():
    s1 = Server()
    s2 = Server()
    s3 = Server()
    
    s1.setNeighbors([s2, s3])
    s2.setNeighbors([s1, s3])
    s3.setNeighbors([s1, s2])
    
    # Add a state machine no one else has
    s2.stateMachine[1] = "test"
    
    # Request an election
    s2.requestVotes()
    
    # Add to the leaders log a command no none else has
    #s2.log.append(("test", 1, False, 0))
    
    assertion(s1.log[-1][0] == "New Term", "Server has the correct log.")
    assertion(s1.log[-1][1] == 1, "Server is in right term.")
    assertion(s3.clusterLeader.uuid == s2.uuid, "Server has the correct leader.")
    assertion(s1.stateMachine[1] == "test", "Server has the correct state machine.")
        

if __name__ == '__main__':
    main()