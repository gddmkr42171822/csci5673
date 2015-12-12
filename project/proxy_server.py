#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
# credit to: http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/
import socket
import select
import time
import sys

blindProxyPort = 8888
blindProxyIP = '' # intentionally an empty string so it binds to all interfaces on machine

coordProxyPort = 8889
coordProxyIP = '' # intentionally an empty string so it binds to all interfaces on machine

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
forward_to = []
# forward_to.append(('localhost', 9000)) # replace this with the ip of responding client
# forward_to.append(('localhost', 9010)) # replace this with the ip of responding client

class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False

class TheServer:
    input_list = []
    channel = {}
    channel_ctrs = {}
    channel_reqs = {}
    responders = []

    def __init__(self, host, port, coord_host, coord_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

        self.coord_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.coord_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.coord_server.bind((coord_host, coord_port))
        self.coord_server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        self.input_list.append(self.coord_server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                # check if this is a new requestor seeking to initiate contact
                if self.s == self.coord_server:
                    self.on_accept_coord()
                    break

                # check if this is a requestor starting a transaction
                if self.s == self.server:
                    # if responders are available, proceed with transaction
                    if len(forward_to) > 0:
                        self.on_accept()
                    else:
                        # not responders are available so bail
                        clientsock, clientaddr = self.server.accept()

                        print clientaddr,"has connected with a request but no responders available. Sending 'unable' message."
                        clientsock.send("unable\n")
                        clientsock.close()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    # if this is from a responder, examine its contents
                    if self.s in self.responders:

                        # figure out what requestor this is in response to
                        cs = self.channel[self.s]

                        # if the responder is unable to find this content, go on to the next one
                        if self.data == "unable\n":
                            # if there are no more responders left to check, send the requestor the bad news
                            # connections will get closed once the requestor terminates the session
                            if self.channel_ctrs[cs] + 1 >= len(forward_to):
                                print "no remaining responders and content not found, sending requestor 'unable' message"
                                self.on_recv()
                            else:
                                # disconnect current forwarder
                                self.input_list.remove(self.s)
                                self.responders.remove(self.s)
                                self.channel[cs].close()
                                del self.channel[cs]
                                del self.channel[self.s]

                                # connect to new forwarder
                                self.channel_ctrs[cs] +=1
                                print "connecting to next responder ({0}:{1}) and sending request".format(
                                    forward_to[self.channel_ctrs[cs]][0], forward_to[self.channel_ctrs[cs]][1])

                                forward = Forward().start(forward_to[self.channel_ctrs[cs]][0], forward_to[self.channel_ctrs[cs]][1])
                                if forward:
                                    self.input_list.append(forward)
                                    self.responders.append(forward)
                                    self.channel[cs] = forward
                                    self.channel[forward] = cs
                                else:
                                    print "Can't establish connection with remote server (2)."

                                # send original request to current responder
                                forward.send(self.channel_reqs[cs])
                        else:
                            self.on_recv()
                    else:
                        # save request for possible future use
                        self.channel_reqs[self.s] = self.data

                        self.on_recv()

    def on_accept(self):
        clientsock, clientaddr = self.server.accept()
        clientsock.send("distrib_ok\n")

        self.channel_ctrs[clientsock] = 0
        forward = Forward().start(forward_to[self.channel_ctrs[clientsock]][0], forward_to[self.channel_ctrs[clientsock]][1])
        if forward:
            print clientaddr, "has connected with a request"

            print "connecting to first available responder ({0}:{1}) and sending request".format(
                forward_to[self.channel_ctrs[clientsock]][0], forward_to[self.channel_ctrs[clientsock]][1])

            # Pop off used responder and re-add it to end of list like a fifo priority queue
            responder = forward_to.pop(0)
            forward_to.append(responder)

            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.responders.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server.",
            print "Closing connection with client side", clientaddr
            clientsock.close()

    def on_accept_coord(self):
        coordsock, coordaddr = self.coord_server.accept()

        coorddata = coordsock.recv(buffer_size)
        if coorddata.startswith("distrib_join "):
            print coordaddr,"has connected as a responder."
            line_arr = coorddata.rstrip("\n").split()
            print "adding {0}:{1} to list of responders".format(coordaddr[0], line_arr[1])
            forward_to.append((coordaddr[0], int(line_arr[1])))

        coordsock.close()

    def on_close(self):
        print self.s.getpeername()," has disconnected."
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        # print "received from remote server: ", data
        self.channel[self.s].send(data)

if __name__ == '__main__':
        server = TheServer(blindProxyIP, blindProxyPort, coordProxyIP, coordProxyPort)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C - Stopping Proxy Server"
            sys.exit(1)