#!/usr/bin/env python
import SocketServer
import hashlib
import os.path
from Crypto.Cipher import AES
from Crypto import Random
import sys

centralServerPort = 7777
centralServerIP = '' # intentionally an empty string so it binds to all interfaces on machine

user_creds = {}
content_keys = {}

class CentralHandler(SocketServer.BaseRequestHandler):
    """
    This gets instantiated upon each request to the server
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # unpack the contents
        #username = self.data[:self.data.index(":")]
        #command = self.data[self.data.index(":")+1:]
        #command_arr = command.split()
        username = 'bob' # Stubbed the username since we may use the code as it is later
        command_arr = self.data.split()
        print 'Command received from IP |{0}|: {1}'.format(self.client_address[0],command_arr)
        if command_arr[0] == "auth":
            authKey = self.doAuth(username, command_arr[1])
            self.request.sendall(authKey)
        elif command_arr[0] == "get":
            # the client is only asking for the content key because it will try to get the actual content from the proxy server
            if command_arr[2] == 'key':
                self.doGetContentKey(username, command_arr[1])
            # the client is asking for both the content key and actual content. it probably was unable to fetch the content from the proxy server
            elif command_arr[2] == 'content':
                self.doGetContentKey(username, command_arr[1])
                self.doGetContent(username, command_arr[1])
        elif command_arr[0] == "put":
            self.doPut(username, command_arr[1])
            self.request.sendall("ok") # TODO maybe something else

        else:
            self.request.sendall('unable\n')

    # attempt to authenticate a username and password. return the key if successful or 'unable' if not
    def doAuth(self, username, password):
        # TODO check password?  do we care?
        #SHA1 is good middle ground for speed, security, and digest length
        #digest = hashlib.sha1()     #Use this version if OpenSSL is not installed
        digest = hashlib.new('SHA1') #This uses OpenSSl and gets better performance
        digest.update(password) # TODO This doesn't need to be a hash, either a symetric key, random string, or nothing. 
        authKey = digest.hexdigest()
        # update our fancy session tracker
        user_creds[username] = authKey # TODO should we use this?
        return authKey


    # Attempt to get the content key of a particular file. 
    # Check if the file is on disk
    # return 'unable' if it does not exist
    def doGetContentKey(self, username, filename):
        print 'Looking for content key for {0}'.format(filename)
        if filename not in content_keys:
            if os.path.exists(filename):
                content_keys[filename] = self.genContentKey(filename)
                self.request.sendall(content_keys[filename]+'\n')
            else:
                print 'The content key and content for {0} does not exist on the server.'.format(filename)
                self.request.sendall('unable\n')
        else:
            self.request.sendall(content_keys[filename]+'\n')
    
    # Return the content of a file either from the database or local file
    # If it doesn't exist return 'unable'
    def doGetContent(self, username, filename):
        print 'Looking for content for {0}'.format(filename)        
        BUF_SIZE = 1024
        block_sz = AES.block_size
        salt = Random.new().read(block_sz - len('Salted__'))
        key_length = 32
        password = 'BlindProxy'     #This is where we'd have auth
        key, iv = self.derive_key_and_iv(password, salt, key_length, block_sz)
        cipher = AES.new(key, AES.MODE_CBC, iv) #AES with block chaining
        try:
            with open(filename, 'rb') as file:
                print 'Serving file {0}'.format(filename)
                self.request.sendall('Salted__' + salt) #Send salt for decrypt
                more = True
                while more:
                    data = file.read(BUF_SIZE * block_sz)
                    if not data or len(data) % block_sz != 0: #Pad last block of data
                        padding_length = block_sz - (len(data) % block_sz)
                        data += padding_length * chr(padding_length)
                        more = False;
                    self.request.sendall(cipher.encrypt(data)) #Encrypt and send data
        except:
            print '{0} does not exist.'.format(filename)
            self.request.sendall('unable\n')


    def derive_key_and_iv(self, password, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = hashlib.md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length + iv_length]

    # attempt to put a filename/content_key tuple into the store
    def doPut(self, username, tuple):
        # TODO auth this request?
        filename = tuple[:tuple.index('/')]
        content_key = self.genContentKey(filename) 
        content_keys[filename] = content_key

    # generate the content key for a given file
    def genContentKey(self, filename):

        digest = hashlib.new('SHA1')
        BUF_SIZE = 32768 #32K
        #Hash the file by chunk, usefull when we test large content
        try:
            with open(filename, 'rb') as file:
                while True:
                    data = file.read(BUF_SIZE)
                    if not data:
                        break
                    digest.update(data)
            return digest.hexdigest()
        except Exception as e:
            print("getContentKey: ", e)


if __name__ == "__main__":
    server = SocketServer.TCPServer((centralServerIP, centralServerPort), CentralHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
            print "Ctrl C - Stopping Server"
            sys.exit(1)
