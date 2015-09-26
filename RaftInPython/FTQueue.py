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
        return self.queue.pop(0)
    
    def top(self):
        '''
        '''
        return self.queue[0]
    
        