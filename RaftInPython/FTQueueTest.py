'''
Created on Sep 25, 2015

@author: Bob
'''
from Server import Server

def assertion(boolean, testName):
    if boolean:
        print(testName + " PASSED")
    else:
        #raise Exception(testName + " FAILED")
        print(testName + " FAILED")


def main():
    print "Running FTQueueTest..."
    label = 5
    item = 10
    s = Server()
    
    # Test the queue creation
    qid = s.create_Queue(label)
    assertion(isinstance(qid, int), "Create queue returned a int as a queue id.")
    
    # Test that the right label returns the right queue id
    assertion(s.get_qid(label) == qid, "Label return the right qid.")
    
    # Test that the queue is the right size
    s.push(qid, item)
    assertion(s.qsize(qid) == 1, "Queue is the right size.")
    
    # Test that the queue retrieves the items in the right order
    s.push(qid, 11)
    assertion(s.pop(qid) == item, "Queue pop returns the right item.")
    assertion(s.top(qid) == 11, "Queue top returns the right item.")
    assertion(s.qsize(qid) == 1, "Queue should not be empty.")
    
    
    
    
    
    

if __name__ == '__main__':
    main()