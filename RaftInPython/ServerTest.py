'''
Created on Sep 25, 2015

@author: Bob
'''
from Server import Server
from Server import ServerState

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
    pass

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
    assertion(s1.log[0][1] == 1, "Server has the right term in the log.")

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
    
    # Add to the leaders log a command no none else has
    s2.log.append(("test", 1, False, 0))
    
    # Add a state machine no one else has
    s2.stateMachine[1] = "test"
    
    # Request an election
    s2.requestVotes()
    
    assertion(s1.log[-1][0] == "test", "Server has the correct log.")
    assertion(s3.clusterLeader.uuid == s2.uuid, "Server has the correct leader.")
    assertion(s1.stateMachine[1] == "test", "Server has the correct state machine.")
        

if __name__ == '__main__':
    main()