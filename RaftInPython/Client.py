'''
Created on Sep 25, 2015

@author: Bob

Client Interaction:
1) Changes from clients go through leader
    i) Client needs to be automatically assigned to the leader
    ii) Should only need to know one node in the cluster
    iii) Client should be in a while true loop and take commands from the command line
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
    
    def waitForCommands(self):
        while True:
            function = raw_input("Enter the function you want to call or 'quit': ")
            if function == "quit":
                return
            elif function == "create_Queue":
                label = raw_input("Enter queue label: ")
                qid = self.clusterLeader.clientCommand(function, int(label))
                print "Newly created queue id is " + str(qid)
            elif function == "get_qid":
                label = raw_input("Enter queue label: ")
                qid = self.clusterLeader.clientCommand(function, int(label))
                print "Queue id is " + str(qid)
            elif function == "push":
                qid = raw_input("Enter qid: ")
                item = raw_input("Enter item: ")
                self.clusterLeader.clientCommand(function, int(qid), int(item))
                print "Pushed {0} onto queue".format(str(item))
            elif function == "pop":
                qid = raw_input("Enter qid: ")
                item = self.clusterLeader.clientCommand(function, int(qid))
                print "Item popped from queue is " + str(item)
            elif function == "top":
                qid = raw_input("Enter qid: ")
                item = self.clusterLeader.clientCommand(function, int(qid))
                print "Top item on queue is " + str(item)
            elif function == "qsize":
                qid = raw_input("Enter qid: ")
                qsize = self.clusterLeader.clientCommand(function, int(qid))
                print "The size of the queue is " + str(qsize)
            elif function == "returnlog":
                log = self.clusterLeader.clientCommand(function)
                print "Leader log contains "
                print log
            else:
                print "That is not a valid function."
                
        
        