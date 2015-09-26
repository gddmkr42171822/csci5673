'''
Created on Sep 25, 2015

@author: Bob

Pseudocode:

1) Server will have a dictionary of queues referenced by QueueID



Concensus Algorithm:
Description
------------
1) Each server will have a state machine and a log 
    The state machine in our case is the queue
2) Each state machine has a log of commands
    Our case all the commands for the queue.
3) Consensus ensures each state machine executes the same commands in the same order

Algorithm
-----------
Leader election:
1) Servers have 3 states: follower, candidate, leader
2) Servers start as followers
3) Servers time out at different rates and become candidates (election timeout) and request votes from the other servers
    i) The first candidate starts the term at 1
    ii) Sends out heartbeats after becoming elected
    iii) When heartbeats fail, a new election occurs all over
    iv) If noone receives the majority of votes a new election occurs
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


class Server(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.queues = {}
        
        
        
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
            
    
                
                
        