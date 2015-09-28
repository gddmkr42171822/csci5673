'''
Created on Sep 25, 2015

@author: Bob
'''
import uuid
from Queue import Queue
from random import randint

class FTQueue(object):
    '''
    classdocs
    '''


    def __init__(self, label):
        '''
        Constructor
        '''
        # Create new queue/list
        self.queue = []
        # Create a unique id
        self.id = randint(0,100)
    
    def put(self, item):
        '''
        '''
        self.queue.append(item)
        
    def qsize(self):
        '''
        '''
        return len(self.queue)
    
    def get(self):
        '''
        '''
        if len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            return 0
    
    def top(self):
        '''
        '''
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return 0
    
        