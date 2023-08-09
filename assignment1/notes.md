## Starting with the commands given on the assignment pdf.

#### 1. `<ifconfig>` : stands for interface configuration and is used to view and change the configuartion of network interface in my system. 
- ifconfig will return a lot of things, to open the specific ines write ifconfig [name] as `ifconfig en0`.
- to disable wifi use `ifconfig en0 down` ans to enable it write `ifconfig en0 up`



#### 2. `gateway` : In computer networking, a gateway is a `network node` (device or software) that serves as an `entry or exit point between two separate networks.` It acts as an intermediary that allows data to flow between networks that use different protocols, addressing schemes, or technologies. 

#### 3. `IP address` : short for `Internet Protocol address,` is a numerical label assigned to each device connected to a computer network that uses the Internet Protocol for communication. IP addresses are essential for `identifying and locating` devices on a network and enabling data transmission between them.

#### 4. `network mask | subnet | netmask`: a 32-bit value used in combination with an IP address to `define the network portion and host portion of the address`. It is a fundamental concept in IP networking and is used to determine which part of the IP address represents the network identifier and which part represents the host identifier. Series of 1 before 0. The network part is identified using the `&` between the mask and ip.


#### 5. `hardware address | MAC address` : 48 bits, 6 pairs of hexadecimal value.


#### 6. `DNS Server` : Domain Name System server.  Its primary purpose is to translate human-readable domain names (such as www.example.com) into machine-readable IP addresses (such as 192.0.2.1). This process is known as DNS resolution or DNS name resolution.



#### 7. `<ping>` : to discover wether a particular IP address is online or not and to measure the round-trip time it takes for a data packet to travel from the source to the destination and  back again. 

- usage : `ping youtube.com`, `ping youtube.com -s packet_size`, `ping youtube.com -t ttl_value`

