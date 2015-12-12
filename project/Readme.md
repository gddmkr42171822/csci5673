# Blind Proxy

## Running the Proxy and Server 
* Start the Proxy and Server
	* ```./server.py```
	* ```./proxy_server.py ```

## Running the Client
* Run the client, all command line parameters are optional
	*  ```./client.py 
					  -h 
					  -r <responder_port>
					  -s <server_hostname> 
					  -p <proxy_hostname> 
					  -u <username> 
					  -l <latency log file> 
					  -t <time messages>```
* Authenticate the client:
	* ```auth <password>```
* Request content:
	* ```get cats.png```
* Turn the client into a responder:
	* ```responder```

## Testing the Blind Proxy Architecture On a Local Machine
* Start the Proxy, Server, and Two Clients
	* ```./proxy_server.py```
	* ```./server.py```
	* ```./client.py``` 
	* ```./client.py```
* Build the cache of the first client then transform into responder:
	* ```get blah.txt #File must be stored locally at the server```
	* ```responder```
* Request content from the proxy with the second client:
	* ```get blah.txt```

**Things To Note**
* Clients should be run from two separate directories
* Clients store the file symmetrically encrypted



