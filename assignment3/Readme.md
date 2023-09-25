Reliable data transfer with congestion control mechanism & yet obtain high throughput 
Implement the client given the system is running !!
# relevent chapters -> Transport layer (chapter 3)


Given UDP server running on `vayu.iitd.ac.in`


How to do (suggested) ??
1. client sends request to server to receive a certain number of bytes from a certain offset. 
(the server replies to client with the data, but makes checks to decide wether to reply or not)


2. How serevr reacts ??
a. randomly decides to not reply every now and then, (uniform random distribution <-> const packet loss rate)
b. To force clients to not send requests too fast, the server implements a leaky bucket filter for each client
c. The server further keeps track of requests that could not be serviced because enough tokens were not available. Can also add penalty to the rude clients 
