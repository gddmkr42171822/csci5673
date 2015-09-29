'''
Created on Sep 25, 2015

@author: Bob
'''
import uuid
from Queue import Queue
from random import randint

class FTQueue(object):
    '''
    FTQueue is supposed to be a distributed object that
    is replicated amoun multiple 'servers'
    '''


    def __init__(self, label):
        '''
        The queue will be represented as a list
        with an id between 0 and 100
        '''
        # Create new queue/list
        self.queue = []
        # Create a unique id
        self.id = randint(0,100)
    
    def put(self, item):
        '''
        Adds an item to the queue
        '''
        self.queue.append(item)
        
    def qsize(self):
        '''
        Returns the size of the queue
        '''
        return len(self.queue)
    
    def get(self):
        '''
        Gets the top item off the queue and returns it
        '''
        if len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            return 0
    
    def top(self):
        '''
        Returns the value of the item on top of the queue
        '''
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return 0
    
        