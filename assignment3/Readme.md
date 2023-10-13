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




Remember that packets can get reordered on the network, so you should not expect to receive replies in
the same order in which you sent. Further, you should not expect to receive a reply to each request
because the server may have decided to drop the request! Or the network may have dropped your
request or reply packet. 


How to run the server ??
`java UDPServer 9801 testcase.txt.1 100 constantrate notournament verbose`