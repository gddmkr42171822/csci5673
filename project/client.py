#!/usr/bin/env python
import socket
from sys import stdin, argv, exit
import SocketServer
import os.path
import datetime
from argparse import ArgumentParser
import hashlib
from Crypto.Cipher import AES

# This is to store keys and file names for reverse lookup (e.g. get(hash/key) will return the files name)
cache = {}

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-s", "--server",    help="server hostname",           default="localhost")
    parser.add_argument("-p", "--proxy",     help="proxy hostname",            default="localhost")
    parser.add_argument("-u", "--user",      help="username",                  default="distrib")
    parser.add_argument("-r", "--responder_port", help="proxy responder port", default=9000)
    parser.add_argument("-l", "--llog",      help="latency log file",          default="latency.log")
    parser.add_argument("-t", "--time",      help="log message rtt",           default=False)
    args = parser.parse_args()
    return args

def printHelp():
    print('Client Help')
    print('Central Server operations:')
    print('auth <password>: authenticate with password ***Not Working***')
    print('get <filename>: get the file in most efficient way possible')
    print('')
    print('Blind Proxy Server operations:')
    print('TBD.....')
    print('')
    print('help: print possible commands')
    print('quit: quit')

# helper method which sends a command to the central server and returns the response
def sendCommandToCentralServer(line):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((centralServerIP, centralServerPort))
    #s.send(username + ":" + line)
    s.send(line)
    content = ''
    content_key = ''
    i = 0
    while True:
        response = s.recv(1024)
        if not response:
            break
        # If it is the first thing received which should be the content key or unable if it doesn't exist
        if i == 0:
            response = response.split('\n', 1)
            # Extract the content key out of what was received
            content_key = response[0]
            # Keep the rest in the remaining response
            response = response[1]
        i += 1
        content += response
    s.close()
    content_key = content_key.strip()
    return content_key, content

# TODO: helper method which sends a command to the blind cache and returns the response
# I'm assuming it will be the same kind of request as the central server
def sendCommandToBlindProxy(line):
    # Catch any problems wit the socket like connection refused
    # when blind proxy is not running
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blindProxyIP, blindProxyPort))

        # if no responders are available, the proxy server will immediately bail with an 'unable' message
        handshake = s.recv(1024)
        if handshake == "unable\n":
            s.close()
            return handshake

        s.send(line)
        content = ''
        while True:
            response = s.recv(1024)
            if response == "distrib_ok": continue  # this is really bad but the handshake was bleeding into the content
            if not response:
                break
            content += response
        s.close()
        return content
    except socket.error, (value,message): 
        if s: 
            s.close() 
        print "Could not open socket with blind proxy: {0}".format(message)
        return "unable\n" 

# execute an authentication request and return the key or None if unsuccessful
def doAuth(password):
    auth_key = sendCommandToCentralServer(password)
    print "auth key = ", auth_key
    if auth_key == 'unable': return None

    return auth_key


def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = hashlib.md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length + iv_length]

# generate the content key for a given file
def verifyContentKey(content_key, content):

        digest = hashlib.new('SHA1')
        digest.update(content)
        return content_key == digest.hexdigest()


def decrypt(enc, password, key_length=32):
    bs = AES.block_size
    salt = enc.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    raw = ''
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(enc.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        raw += chunk

    return raw


# write content to the filesystem
def writeFile(filename, content, content_key, server_name):
    f = open(filename, 'wb')
    # Write the content to the file sent by the server
    f.write(content)
    f.close()
    with open(filename, 'rb') as file:
        raw = decrypt(file, 'BlindProxy')
    if verifyContentKey(content_key, raw):
        print 'Content integrity verified...caching encrypted content.'
        cache[content_key] = filename

    #print 'Content key: {0}'.format(content_key)



# execute a put request for a filename and content_key
def doPut(line):
    # TODO this method should accept a filename and content_key and be concat'd with a '/'
    sendCommandToCentralServer(line)

class CentralHandler(SocketServer.BaseRequestHandler):
    """
    This gets instantiated upon each request to the server
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # Split the request on space and put it in a list
        self.data = self.data.split()
        print 'Command received from IP |{0}|: {1}'.format(self.client_address[0],self.data)
        # Check if the client has the filename
        if self.data[1] in cache:
            filename = cache[self.data[1]]
            # If the file exists send the contents to the requester
            if os.path.isfile(filename):
                f = open(filename, 'rb') # opens file in binary format
                file_content = f.read(1024)
                while(file_content):
                    self.request.sendall(file_content)
                    file_content = f.read(1024)
                f.close()
                print 'Served file {0}'.format(filename)
            else:
                self.request.sendall('unable\n')
        else:
            self.request.sendall('unable\n')

# Command line argument parser
args = parse_args()

# The port and ip for the central server
centralServerPort = 7777
centralServerIP = args.server

# The port and ip for the blind proxy cache
blindProxyPort = 8888
blindProxyCoordPort = 8889
blindProxyIP = args.proxy

# Get the username & password
username = args.user

# The port which this client will be listening to if a responder
responderPort = int(args.responder_port)

# read commands until 'quit' received
try:
    while True:
        line = stdin.readline()
        lineArr = line.rstrip("\n").split()

        # execute the proper command
        if lineArr[0] == "help":
            printHelp()
        # TODO: Authentication is disabled for now until we figure out what to do for it
        #elif lineArr[0] == "auth":
                #authKey = doAuth(line)
                # TODO check authKey?
        elif lineArr[0] == "get":
            #Declare empty strings for storing the time a message is sent and received
            timeReceived = ""
            timeSent = ""
            #TODO: Authentication is disabled for now until we figure out what to do for it
            #if not authKey:
                #print "Unable to execute command, please authenticate first" # TODO should we do this in client?
                #continue
            # If we are getting the content through the proxy on the LAN
            if args.time: # Start request time
                t = open(args.llog, 'a')
                timeSent = datetime.datetime.now().time().strftime("%H:%M:%S.%f")

            # get the content key from the central server
            content_key, content = sendCommandToCentralServer(line + " key")
            if content_key != 'unable':
                # try to get content from proxy server
                content = sendCommandToBlindProxy('get ' + content_key)
                if content != 'unable\n':
                    # the proxy server satisfied the request
                    writeFile(lineArr[1], content, content_key, "proxy")
                else:
                    # since the proxy server cannot locate the content, get it from the central server
                    #print 'Blind proxy did not reply with content for content key {0}'.format(content_key)
                    print 'Blind proxy did not reply with content.'
                    print 'Checking central server for content...'

                    content_key, content = sendCommandToCentralServer(line + " content")
                    if content_key != 'unable' and content != 'unable\n':
                        print 'Central server has content.'
                        writeFile(lineArr[1], content, content_key, "central")
                    else:
                        print 'Central server does not have the content key or content for {0}.'.format(lineArr[1])
            else:
                print 'Central server does not have the content key or content for {0}.'.format(lineArr[1])
                
            if args.time: # End request time
                timeReceived = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
                t.write('Time sent: {0} Time received: {1}\n'.format(timeSent, timeReceived))
                timeSent = datetime.datetime.strptime(timeSent, "%H:%M:%S.%f")
                timeReceived = datetime.datetime.strptime(timeReceived, "%H:%M:%S.%f")
                t.write('Latency: {0}\n'.format(timeReceived-timeSent))
                t.close()
                print 'Time sent: {0} Time received: {1}'.format(timeSent, timeReceived)
                print 'Latency: {0}'.format(timeReceived-timeSent)
                
        elif lineArr[0] == "put": # TODO this does not need to be called manually. remove once integrated
            # TODO: Authentication is disabled for now until we figure out what to do for it
            #if not authKey:
                #print "Unable to execute command, please authenticate first" # TODO should we do this in client?
                #continue
            doPut(line)

        elif lineArr[0] == "responder": #Add this to the REPL so we can build a cache first
            print 'Client is now a responder.'

            # tell the blind proxy server that this client is now a responder and specify which port it expects traffic on
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((blindProxyIP, blindProxyCoordPort))
            s.send("distrib_join " + str(responderPort) + "\n")
            s.close()

            cache_server = SocketServer.TCPServer(('', responderPort), CentralHandler) # IP intentionally an empty string so it binds to all interfaces on machine
            cache_server.serve_forever()
            break      

        elif lineArr[0] == "print":
            # Print out the cache
            for k,v in cache.items():
                print k,' ',v
            break           
        elif lineArr[0] == "quit":
            # Close the latency file
            f.close()
            break
except KeyboardInterrupt:
    print "Ctrl C - Stopping Client"
    exit(1)
