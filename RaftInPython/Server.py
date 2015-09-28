'''
Created on Sep 25, 2015

@author: Bob

Pseudocode:

1) Server will have a dictionary of queues referenced by QueueID



Concensus Algorithm:
Attributes of servers
------------
1) Each server will have a state machine *completed*
    The state machine in our case is the queue
2) Each state machine has a log of commands *completed*
    Our case all the commands for the queue.
3) Servers have 3 states: follower, candidate, leader *Completed*
4) Each server has a timer that times out between 150 to 300 ms, goes to candidate state, and starts an election *Delayed*
    Multithreaded timer?

Algorithm
-----------
Consensus ensures each state machine executes the same commands in the same order

Leader election:
1) Servers start as followers *Completed*
2) Servers time out at different rates and become candidates (election timeout) and request votes from the other servers
    i) The first candidate starts the term at 1 *Completed*
    ii) Sends out heartbeats after becoming elected *Completed*
    iii) When heartbeats fail, a new election occurs all over *NOT STARTED*
    iv) If no one receives the majority of votes a new election occurs *NOT STARTED*
3) Nodes reply with votes, the server with the most votes becomes the leader *Completed*

Log Replication:
1) Each command is added to the leaders log *NOT STARTED*
    i) initially each command in uncommitted in leaders log
    ii) to commit the entry the leader sends append entries (heartbeats) to followers and awaits replies from majority of nodes
        after they have written the entry
    iii) leader then commits and notifies followers to commit and a response is sent to the client
2) If there are two leaders, the one with the higher term takes over and everyone rolls back their log to imitate the new leader *NOT STARTED*
3) Candidate votes for itself and requests votes *COMPLETED*
4) Followers duplicate leaders log, state machine *COMPLETED*

'''
from FTQueue import FTQueue
import uuid
import time


class Server(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.uuid = str(uuid.uuid4())
        
        # A dictionary of queues
        self.stateMachine = {}
        
        # The server state
        self.state = ServerState.follower
        
        # The log is a list of tuples of commands associated with a term number and committed or not
        # initialize the log to the first term
        # (Command, Term, Commited?, Number of Acknowledgments)
        self.log = [("", 1, True, 0)]
        
        # Boolean for whether this server voted or not
        self.voted = False
        
        # Number of votes the server has received
        self.votesReceived = 0
        
        # Cluster leader uuid
        self.clusterLeader = None
        
        # Tell the server if it should create an election or not
        self.timeout = False
        
        # Kill this server
        self.kill = False
    
    def electionTimeout(self):
        '''
        '''
        while True:
            if self.state == ServerState.leader:
                if self.kill:
                    break
                else:
                    self.sendHeartbeat()
            elif self.timeout:
                print self.uuid + " is requesting a vote."
                self.requestVotes()
            else:
                self.timeout = True
                time.sleep(3)
                
    def removeSelfFromCluster(self):
        for neighbor in self.neighbors:
            if self in neighbor.neighbors:
                neighbor.neighbors.remove(self)
            
    def setNeighbors(self, neighbors):
        # A list of neighbors (server objects), would use a dictionary if we were keeping track of ports and ip's
        self.neighbors = neighbors
        # The server should include itself in the list of neighbors
        self.neighbors.append(self)
                
    def requestVotes(self):
        '''
        '''
        # Change into a candidate to ask for votes
        self.state = ServerState.candidate
        
        # Go through each neighbor object and request their votes
        # Send them a term number to help determine if the server needs to step down as leader
        if self.neighbors:
            for neighbor in self.neighbors:
                neighbor.receiveVoteRequest(self, self.log[-1][1])
            
    def receiveVoteRequest(self, requester, term):
        '''
        '''
        # Check if this server has already sent out a vote
        if not self.voted and self.kill == False:
            # Acknowledge that the candidate was voted for
            requester.acknowledgeVoteRequest()
            self.voted = True
            print self.uuid + " has voted for " + requester.uuid + "."
        elif self.kill:
            print "Server cannot vote because it is dead."
        else:
            print self.uuid + " has already voted."
    
    def acknowledgeVoteRequest(self):
        '''
        '''
        self.votesReceived += 1
        # If this server gets the majority of the votes it should become the leader
        if self.votesReceived >= (len(self.neighbors) - 1) and self.state != ServerState.leader:
            self.state = ServerState.leader
            print self.uuid + " became the leader."
        
            
            self.sendHeartbeat()
    
    def appendEntries(self, clusterLeader, log, stateMachine):
        # Set the leader of the cluster
        self.clusterLeader = clusterLeader
        
        # Set the other servers involved in the election to followers
        if clusterLeader is not self:
            self.state = ServerState.follower
        
        # Force the followers to duplicate the leader's log
        self.log = log
                
        # Force the followers to duplicate the leader's state machine
        self.stateMachine = stateMachine
        
        # Set the timeout of the followers to false
        self.timeout = False
        
        # Followers vote should be false for next election
        self.voted = False
        
        # Reset the votes this server has received
        self.votesReceived = 0
        
        # TODO: Acknowledge to the leader entry or entries were appended   
        # TODO: Commit the entries? 
    
    def sendHeartbeat(self):
        # Send appendMessage to other neighbors to tell them this server is the leader
        # and to make sure they have the right state machine and logs
        for neighbor in self.neighbors:
            neighbor.appendEntries(self, self.log, self.stateMachine)
    
    def clientCommand(self, function, *args):
        '''
        '''
        if function == "create_Queue":
            self.log.append(("{0} {1}".format(function, args[0]), self.log[-1][1], False, 0))
            self.sendHeartbeat()
            return self.create_Queue(args[0])
        elif function == "get_qid":
            self.log.append(("{0} {1}".format(function, args[0]), self.log[-1][1], False, 0))
            self.sendHeartbeat()
            return self.get_qid(args[0])
        elif function == "push":
            self.log.append(("{0} {1} {2}".format(function, args[0], args[1]), self.log[-1][1], False, 0))
            self.sendHeartbeat()
            return self.push(args[0], args[1])
        elif function == "pop":
            self.log.append(("{0} {1}".format(function, args[0]), self.log[-1][1], False, 0))
            self.sendHeartbeat()
            return self.pop(args[0])
        elif function == "top":
            self.log.append(("{0} {1}".format(function, args[0]), self.log[-1][1], False, 0))
            self.sendHeartbeat()
            return self.top(args[0])
        elif function == "qsize":
            self.log.append(("{0} {1}".format(function, args[0]), self.log[-1][1], False, 0))
            return self.qsize(args[0])
        elif function == "returnlog":
            return self.log
        elif function == "kill":
            self.removeSelfFromCluster()
            self.kill = True
        
    def create_Queue(self, label):
        '''
        TODO: Docstrings
        '''
        # If we don't already have a queue with this label
        if label not in self.stateMachine:
            # Associate a label with a new queue of integers
            # Queues could be created with same qid
            self.stateMachine[label] = FTQueue(label)
            # Get the queue id from the new queue and return it
            queueID = self.stateMachine[label].id
            return queueID
        else:
            print "Queue has already been created."
            return 0
       
        
    def get_qid(self, label):
        '''
        TODO: Docstrings
        '''
        
        # Get the queue id from the queue associated with the label and return it
        queueID = self.stateMachine[label].id
        return queueID
    
    def push(self, queueID, item):
        '''
        TODO: Docstrings
        '''
        # Find the queue associated with the queueID
        for key in self.stateMachine:
            if self.stateMachine[key].id == queueID:
                # Put the item in the bottom of the queue
                self.stateMachine[key].put(item)
                return
    
    def pop(self, queueID):
        # Find the queue associated with the queueID
        for key in self.stateMachine:
            if self.stateMachine[key].id == queueID:
                # Returns the first item on the queue
                return self.stateMachine[key].get()
            
    def top(self, queueID):
        # Find the queue associated with the queueID
        for key in self.stateMachine:
            if self.stateMachine[key].id == queueID:
                # Returns the first item on the queue
                return self.stateMachine[key].top()
    
    def qsize(self, queueID):
        # Find the queue associated with the queueID
        for key in self.stateMachine:
            if self.stateMachine[key].id == queueID:
                # Return the size of the queue
                return self.stateMachine[key].qsize()
            
'''
This class specifies the states a server can be in
'''
class ServerState:
    follower = 1
    candidate = 2
    leader = 3
                
        