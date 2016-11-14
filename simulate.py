import sys
import node
import sink
import time
from Queue import Queue
from q_class import Queues
import logging
from logrecord import LogRecord

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#neighbor_dict = {1: [2,3], 2: [4,5], 3: [6], 4: [7], 5: [7], 6:[8], 7:[9], 8: [9], 9:[]}

lines = open('topology_information.txt').read().splitlines()
coordinates_dict = eval(lines[0])
import json
temp_neighbor_dict = json.loads(lines[1])
neighbor_dict = {}
for item in temp_neighbor_dict.items():
	neighbor_dict.update({int(item[0]):item[1]})

#coordinates_dict = {1: (2,3), 2: (4,2), 3: (1,1), 4: (8,11), 5: (13,6), 6: (3,14), 7: (4,2), 8: (4,6), 9: (3,5)}
sink_node = 60
neighbor_dict[sink_node] = []
#simulation_num = 4
import threading

neighbor_dict[sink_node]

def start_simulation(ndict, cdict, sink_node):
	lrec = LogRecord('packetlogger.txt')
	lrec.truncate_log()
	beginner_node = 1
	queues = Queues()
	#Create dissipation event
	dissipation_event = threading.Event()
	transmission_event = threading.Event()
	transmission_done_event = threading.Event()
	#initialize the beginner, node and the sink threads
	try:
		for nod in neighbor_dict:
			if nod == beginner_node:
				bthread = node.Node(beginner_node, cdict[beginner_node], ndict, queues, dissipation_event, transmission_event,True)
			else:
				exec("Thread_" + str(nod) + " = node.Node(" + str(nod) + ", " + str(cdict[nod]) + ",ndict, queues, dissipation_event, transmission_event)")
	except Exception:
		print "Thread already started"
	#Get the node level dictionary of all nodes according to their neighbors
	node_level_dict = thread_start_order(ndict,beginner_node)
	for keyy in node_level_dict:
	#Get unique values of node IDs in the list
		node_set = set(node_level_dict[keyy])
		unique_node_list = list(node_set)
		node_level_dict.update({keyy: unique_node_list})
	
	#Start the beginner thread
	bthread.start()	
	time.sleep(1)

	#Start rest of the threads level-wise
	wait_constant = 0.2
	popped_level_0 = node_level_dict.pop(0)
	for key in node_level_dict:
		for every_node in node_level_dict[key]:
			try:
				thname = "Thread_" + str(every_node)
				exec("alive_status = " + thname + ".isAlive()")
				if not alive_status:
					exec("Thread_" + str(every_node) + ".start()")
			except Exception:
				print "Thread already started"
		time.sleep(wait_constant*key)
	
	
	sthread = sink.Sink(sink_node, cdict[sink_node], ndict, queues, dissipation_event, transmission_event, transmission_done_event)
	print "Starting the sink node"
	sthread.start()
	result = start_transmission(queues, transmission_event)
	transmission_done_event.wait()
	return
	


def start_transmission(queues, transmission_event):
	count = 0
	for i in range(150000):
		count = count+1
	start_trans = raw_input("Do you want to start Data Transmission?\n")
	if str(start_trans) in ['y', 'Y', 'yes', 'Yes','start', 'Start']:
		node_num_transmit = raw_input("Enter the node number to start transmission\n")
		if (int(node_num_transmit) not in neighbor_dict.keys() or int(node_num_transmit) == sink_node):
			print "The node number is invalid. Try again."
			return
		else:
			import random
			run_sim_time = raw_input("Enter the time duration for running the simulation\n")	
			exec("start_transmit_q = queues.get_from_repository(" + "'" +"q_" + str(node_num_transmit)+ "'" + ")")
			transmit_que_obj = queues.get_object_by_name(start_transmit_q)
			sim_time = run_sim_time*100
			pkt_num =1
			for sim_time_sec in sim_time:
				data_to_transmit= random.randrange(1023)
				from DataPacket import DataPacket
				data_pkt = DataPacket(data_to_transmit)
				data_pkt.packet_id = generate_uuid()
				print "Data Packet  " +  str(pkt_num)  + " sent"
				transmit_start_status = queues.put_to_queue(transmit_que_obj, data_pkt)
				pkt_num = pkt_num +1
			transmission_event.set()
	return True

def timer_callback():
	print "The timer called back"
	return

def thread_start_order(ndict, beginner):
	print "inside thread start order"
	pop_list = [beginner]
	visited_list = []
	total_node_list = ndict.keys()
	pop_value = 1
	level = 0
	level_dict = {}
	while (len(visited_list)<(len(total_node_list)-1)):
		now_list = []
		for i in range(pop_value):
			now_list.append(pop_list.pop())
		level_dict[level]= now_list
		level=level+1
		for i in now_list:
			pop_list.extend(ndict[i])	
			pop_value = len(pop_list)
			for p in pop_list:
				if p not in visited_list:
					visited_list.append(p)
	#return visited_list
	return level_dict
	

def generate_uuid():
		import uuid
		str_uuid_full = str(uuid.uuid4()).split('-')
		pkt_id = str_uuid_full[len(str_uuid_full)-1]
		return pkt_id

if __name__ == '__main__':
	print "Staring Simulation..."
	#result = thread_start_order(neighbor_dict, 1)
	result = start_simulation(neighbor_dict, coordinates_dict, sink_node)
	if result:
		print "Simulation successful"
