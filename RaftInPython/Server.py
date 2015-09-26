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
4) Each server has a timer that times out between 150 to 300 ms, goes to candidate state, and starts an election *In Progress*
    Multithreaded timer?

Algorithm
-----------
Consensus ensures each state machine executes the same commands in the same order

Leader election:
1) Servers have 3 states: follower, candidate, leader
2) Servers start as followers
3) Servers time out at different rates and become candidates (election timeout) and request votes from the other servers
    i) The first candidate starts the term at 1
    ii) Sends out heartbeats after becoming elected
    iii) When heartbeats fail, a new election occurs all over
    iv) If no one receives the majority of votes a new election occurs
4) Nodes reply with votes, the server with the most votes becomes the leader
5) Changes from clients go through leader
6) Each command is added to the leaders log
    i) initially each command in uncommitted in leaders log
    ii) to commit the entry the leader sends append entries (heartbeats) to followers and awaits replies from majority of nodes
        after they have written the entry
    iii) leader then commits and notifies followers to commit and a response is sent to the client
7) If there are two leaders, the one with the higher term takes over and everyone rolls back their log to imitate the new leader

'''
from FTQueue import FTQueue
from threading import Thread, Semaphore
import time


class Server(object):
    '''
    classdocs
    '''


    def __init__(self, neighbors):
        '''
        Constructor
        '''
        # A dictionary of queues
        self.queues = {}
        # The server state
        self.state = ServerState.follower
        # A list of neighbors (server objects), would use a dictionary if we were keeping track of ports and ip's
        self.neighbors = neighbors
        # The log is a list of tuples of commands associated with a term number
        # initialize the log to the first term
        self.log = [('', 1)]
        
        # Boolean for whether this server voted or not
        self.voted = False
        
        # Keep track of the time until the election timeout
        #self.timerStart = 0
        #self.timerEnd = 0
        #self.timerLock = Semaphore()
        #self.timerLock.acquire()
        # Create a thread to run the election timer
        # A list of the threads running in the program
        #self.threads = []
        #self.startElectionTimerThreads()
        #self.runElectionTimer()
    
    def startElectionTimerThreads(self):
        worker = Thread(target=self.runElectionTimer)
        worker.start()
        self.threads.append(worker)
        print "Started election timer thread."
        #worker = Thread(target=self.changeServerState)
        #worker.start()
        #self.threads.append(worker)
        #print "Started change server state thread."
    
    def changeServerState(self):
        while True:
            self.timerLock.acquire()
            #if self.state == ServerState.follower:
            #print "Changing server state to candidate."
            self.state = ServerState.candidate
            # TODO: Create a new election
            
        
    def runElectionTimer(self):
        while True:
            if self.timerStart == 0:
                self.timerStart = time.time()
            self.timerEnd = time.time()
            c = self.timerEnd - self.timerStart
            #sys.exit()
            # Keep track of the time and make server
            # state changes after 3 seconds (3000 milliseconds)
            if c >= 3:
                self.timerLock.release()
                self.timerStart = 0
                
                
    def requestVotes(self):
        '''
        '''
        # Go through each neighbor object and and request their votes
        # Send them a term number to help determine if the server needs to step down as leader
        for neighbor in self.neighbors:
            neighbor.receiveVoteRequest(self, self.log[-1][1])
            
    def receiveVoteRequest(self, requester, term):
        '''
        '''
        # Check if this server needs to be overriden by a server with a greater term
        if term > self.log[-1][1] and self.state.leader:
            self.state = ServerState.follower
            #TODO: Get entries from new leader
        # Check if this server has already sent out a vote
        elif not self.voted:
            # Acknowledge that the candidate was voted for
            requester.acknowledgeVote()
            self.voted = True
            
        
        
    def create_Queue(self, label):
        '''
        TODO: Docstrings
        '''
        # If we don't already have a queue with this label
        if label not in self.queues:
            # Associate a label with a new queue of integers
            self.queues[label] =  FTQueue(label)
            # Get the queue id from the new queue and return it
            queueID = self.queues[label].id
            return queueID
       
        
    def get_qid(self, label):
        '''
        TODO: Docstrings
        '''
        
        # Get the queue id from the queue associated with the label and return it
        queueID = self.queues[label].id
        return queueID
    
    def push(self, queueID, item):
        '''
        TODO: Docstrings
        '''
        # Find the queue associated with the queueID
        for key in self.queues:
            if self.queues[key].id == queueID:
                # Put the item in the bottom of the queue
                self.queues[key].put(item)
                return
    
    def pop(self, queueID):
        # Find the queue associated with the queueID
        for key in self.queues:
            if self.queues[key].id == queueID:
                # Returns the first item on the queue
                return self.queues[key].get()
            
    def top(self, queueID):
        # Find the queue associated with the queueID
        for key in self.queues:
            if self.queues[key].id == queueID:
                # Returns the first item on the queue
                return self.queues[key].top()
    
    def qsize(self, queueID):
        # Find the queue associated with the queueID
        for key in self.queues:
            if self.queues[key].id == queueID:
                # Return the size of the queue
                return self.queues[key].qsize()
            
'''
This class specifies the states a server can be in
'''
class ServerState:
    follower = 1
    candidate = 2
    leader = 3
                
        