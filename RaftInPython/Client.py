'''
Created on Sep 25, 2015

@author: Bob
'''
class Client(object):
    '''
    classdocs
    '''


    def __init__(self):
        self.clusterLeader = None
        
    def connectClientToLeader(self, server):
        if server.clusterLeader:
            self.clusterLeader = server.clusterLeader
            return
        print "Could not find the cluster leader."
        
        