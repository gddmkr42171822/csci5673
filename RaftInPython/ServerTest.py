'''
Created on Sep 25, 2015

@author: Bob
'''
from Server import Server
from Server import ServerState
import time

def assertion(boolean, testName):
    if boolean:
        print(testName + " PASSED")
    else:
        print(testName + " FAILED")
        
def main():
    #testInitialServerState()
    #testServerTimer()

def testInitialServerState():
    s = Server({})
    assertion(s.state == ServerState.follower, "Server should start in the follower state.")

def testServerTimer():
    s = Server({})
        

if __name__ == '__main__':
    main()