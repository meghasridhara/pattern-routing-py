import threading
import sys, os
import InitialRoutePacket
import logging
import time
from DataPacket import DataPacket
from logrecord import LogRecord


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Sink (threading.Thread):
	def __init__(self, nodeID, coordinates,neighbor_dict, q_obj, dissipation_event, transmission_event, transmission_done_event):
		threading.Thread.__init__(self)
		self.nodeID = nodeID
		self.coordinates = coordinates
		self.neighbor_dict = neighbor_dict
		self.q_obj = q_obj
		self.dissipation_event =  dissipation_event
		self.transmission_event = transmission_event
		self.transmission_done_event = transmission_done_event
		self.sink_pattern = '51NK'
		self.pend_on_queue_time = 600
		self.packet_logger = LogRecord('packetlogger.txt')
		self.sent_flag = 'SENT'
		self.received_flag = 'RCVD'

	def run(self):
		init_sink_list = []
		exec("pop_queue = self.q_obj.get_from_repository(" + "'" +"q_"+str(self.nodeID)+ "'" +")")
		exec("q_size = self.q_obj.get_qsize(" + "'" +str(pop_queue) + "'" + ")")
		
		for i in range (q_size):
			exec ("init_route_packet = self.q_obj.get_from_queue(" + "'" +str(pop_queue) +"'" + ")")
			pkt_id = init_route_packet.packet_id
			log_msg= self.packet_logger_message(pkt_id, "r", 'RCVD', 'INIT_ROUTE')
			self.packet_logger.write_log(log_msg)
			init_sink_list.append(init_route_packet)

		self.all_routes_dict = self.condense_packets_store_seeds (init_sink_list)
		self.maps_to_route_id = self.map_nodes_to_route_id(self.all_routes_dict, self.neighbor_dict)
		self.routes_for_nodes = self.decide_routes_for_nodes(self.maps_to_route_id, self.all_routes_dict)
		self.final_path_list = self.get_full_paths(self.routes_for_nodes, self.all_routes_dict)
		self.create_and_store_pattern(self.final_path_list)
		self.create_push_pattern_packets()
		exec("self.queue = self.q_obj.get_from_repository(" + "'" +"q_" + str(self.nodeID)+ "'" + ")")
		self.queue = self.q_obj.get_object_by_name(self.queue)
		self.transmission_event.wait()
		pkt_to_forward = self.pend_on_queue(self.queue, self.pend_on_queue_time)	
		return

	def pend_on_queue(self, q_,timeout, sleeptime = 0):
		retrieved_get = None
		while (sleeptime<timeout):
			time.sleep(0.1)
			if q_.empty():
				sleeptime = sleeptime+1
				timeout = timeout-1

				print "Queue Empty. Pending again"
				retrieved_get = self.pend_on_queue(q_, timeout,sleeptime)
			else:
				retrieved_get = q_.get_nowait()
				logging.debug("%s: Received packet from the queue", str(self.nodeID))
				if isinstance(retrieved_get, DataPacket):
					if (retrieved_get.get_pattern()[len(retrieved_get.get_pattern())-1] == self.sink_pattern):
						packet_data = retrieved_get.get_data()
						packet_sender = retrieved_get.get_pattern()[0]
						pkt_id = retrieved_get.packet_id
						log_msg= self.packet_logger_message(pkt_id, packet_sender, 'RCVD', 'DATA')
						self.packet_logger.write_log(log_msg)
						retrieved_get = self.pend_on_queue(q_, timeout,self.pend_on_queue_time)
		return retrieved_get

	def condense_packets_store_seeds (self, full_pkt_list):
		self.seed_dict = {}
		return_dict = {}
		condensed_list = []
		for item in full_pkt_list:
			condensed_list_item = []
			for node_x in item.get_packet():
				self.seed_dict.update({node_x[0]: node_x[1]})
				condensed_list_item.append(node_x[0])
			condensed_list.append(condensed_list_item)
		route_id  = 1
		for item in condensed_list:
			return_dict.update({route_id: item})
			route_id = route_id+1
		return return_dict
		
			 
	def map_nodes_to_route_id (self,initial_packet_dict, neighbor_dict):
		all_nodes = neighbor_dict.keys()
		visited_nodes = []
		every_node_to_sink = []
		node_and_route_id = {}
		for node_x in all_nodes:
			rid_length_dict= {}
			for route in initial_packet_dict.items():
				update_value = {}
				if node_x in route[1]:
					inx = route[1].index(node_x)
					rid_length_dict.update({route[0] : len(route[1][inx:])})
					min_path = min(rid_length_dict.values())
				for route in rid_length_dict.items():
					if route[1] == min_path:
						update_value = {node_x:route[0]}
					break
				node_and_route_id.update(update_value)
		return node_and_route_id


	def decide_routes_for_nodes (self,node_to_route_dict, ini_dict):
		self.final_list = []
		for value in node_to_route_dict.items():
			exec("route_" + str(value[1]) + " = []")
		temp_iter_list = list(set(node_to_route_dict.values()))
		for route_ in temp_iter_list:
			for val in node_to_route_dict.items():
				if route_ == val[1]:
					exec("route_"+ str(val[1]) + ".append(" + str(val[0]) + ")")
			exec("self.final_list.append(route_" + str(route_) + ")")
		return self.final_list

	def get_full_paths (self,ntor_list, ini_dict):
		route_ = 1
		final_path_list = []
		for item in ntor_list:
			for node_x in item:
				for n in ini_dict[route_]:
					if node_x == n:
						path_tmp = ini_dict[route_][ini_dict[route_].index(n):]
						final_path_list.append(path_tmp)
						break
				route_ = route_ +1
				break
		return final_path_list

	def create_and_store_pattern(self, final_path_list):
		import random
		import string
		self.path_pattern_dict = {}
		self.next_node_dict = {}
		for seed_item in self.seed_dict.items():	
			alpha = random.choice(string.letters)
			new_seed = str(seed_item[1]) + alpha
			self.seed_dict.update({seed_item[0]: new_seed})
		node_pattern = ''
		self.seed_dict.update({self.nodeID: self.sink_pattern})
		for path in final_path_list:	
			for node_ in path:
				node_pattern = node_pattern + str(self.seed_dict[node_])
				self.path_pattern_dict.update({node_pattern:node_})
				try:
					self.next_node_dict.update({node_:path[path.index(node_)+1]})
				except IndexError:
					self.next_node_dict.update({node_:self.nodeID})
		return

	def create_push_pattern_packets(self):
		from PatternPacket import PatternPacket

		self.q_rep = self.q_obj.get_q_repository()
		for node_ in self.next_node_dict:
			#if node id is beginner, delay sending the pattern packets. When node 1 receives the pattern, clear the dissipation event
			#creating pattern packets
			exec("pkt_" + str(node_) + " = PatternPacket (" + "'" + str(self.seed_dict[node_]) + "'" + ", " + "'" +str(self.seed_dict[self.next_node_dict[node_]]) + "'" + ")")
			exec ("pkt_" + str(node_) + ".packet_id = self.generate_uuid()")
			#pushing pattern packets to queues
			qname = 'q_' + str(node_)
			
			if qname in self.q_rep.keys():
				queue_obj = self.q_rep[qname]
				exec("pkt_id = pkt_" + str(node_) + ".packet_id")
				exec( "status = self.q_obj.put_to_queue( queue_obj " + ", " + "pkt_" + str(node_) + ")")
				log_msg= self.packet_logger_message(pkt_id, str(node_) , 'SENT', 'PATTERN')
				self.packet_logger.write_log(log_msg)
		self.dissipation_event.set()
		return
			
		
	def packet_logger_message(self, pktid, to_, sent_or_received, pkt_type):
		message = ""
		if sent_or_received == self.sent_flag:
			message = pktid + "  " + pkt_type + "  " + str(self.nodeID) + "  " +str(to_) + "  " + sent_or_received +  "\n"
		elif sent_or_received == self.received_flag:
			message = pktid + "  " + pkt_type + "  " + str(to_) + "  " + str(self.nodeID) + "  "  + sent_or_received +	"\n"
		return message

			 
		
	def generate_uuid(self):
		import uuid
		str_uuid_full = str(uuid.uuid4()).split('-')
		pkt_id = str_uuid_full[len(str_uuid_full)-1]
		return pkt_id
	
		


				
				
				
			
		


		






