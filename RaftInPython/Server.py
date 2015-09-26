'''
Created on Sep 25, 2015

@author: Bob

Pseudocode:

1) Server will have a dictionary of queues referenced by QueueID
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
                break
    
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
            
    
                
                
        