# pattern-routing-py

#author: Megha Sridhara 

The Pattern Routing Simulator project aims to do the following:
Create a 60-node wireless network, boot up the nodes and route data packets from a source to the sink based on Pattern matching.

How it works:
Node (node.py) and Sink (sink.py) are Python classes that simulate the behavior of participating nodes and sink respectively. 
The three packet types are InitialRoutePacket, PatternPacket and DataPacket. 
On startup, the beginner node sends an InitialRoutePacket to its neighbors and the neighbors in turn append their own
co-ordinates in the packet. 
Every path in the network would thus be represented by a unique list of InitialRoutePackets. 
The sink, upon receiving the same, decides the shortest path and distributes unique patterns via PatternPacket for every node. 

On data transmission, the DataPacket consists of patterns that contain the order of routing. 
Every node pops the pattern and matches it to its own to decide whether to transmit. 

The LogRecord (logrecord.py) takes responsibility of writing the packet movement information into packetlogger.txt.
packetlogger has the format "Packet_id     Packet_name    Sender    Receiver   Send/Recv_flag".
The wireless Radio is simulated as Queues (q_class.py). 

How to run:
>>python simulate.py

...

...

...


>>Do you want to start data transmission?

Y

>>Enter the node number to start transmission

15  

>>Enter the time duration for running the simulation (represents a factor of simulation time ticks) 

10       

...

...

>>pending on the queue

>>pending on the queue


>>^Z

After simulation, the queue becomes empty but the sink still keeps pending on the queue. 
Press Ctrl+Z to stop.

Look through the packetlogger.txt to check the packet log. 
Run the analysis to get the packet delivery ratio. 

>>python anaysis.py










