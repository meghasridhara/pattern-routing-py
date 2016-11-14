import threading
import time
import sys, os
from InitialRoutePacket import InitialRoutePacket
import logging
from copy import deepcopy
from DataPacket import DataPacket
import Queue
import uuid
from logrecord import LogRecord

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Node (threading.Thread):
	def __init__(self, nodeID, coordinates, neighbor_dict, q_obj, dissipation_event,  transmission_event, beginner= False):
		threading.Thread.__init__(self)
		self.nodeID = nodeID
		self.coordinates = coordinates
		self.neighbor_dict = neighbor_dict
		self.beginner=beginner
		self.q_obj = q_obj
		self.dissipation_event = dissipation_event
		self.transmission_event = transmission_event
		self.queue = None
		self.pend_on_queue_time = 480
		self.packet_types = {1: 'INIT_ROUTE', 2: 'PATTERN', 3: 'DATA' }
		self.packet_logger = LogRecord('packetlogger.txt')
		self.sent_flag = 'SENT'
		self.received_flag = 'RCVD'

	def run(self):
		logger.debug ("Booted node: %s", str(self.nodeID) )
		self.q_list, self.neighbor_qname_list = self.create_neighbor_queues()
		if self.beginner:
			q = 'q_' + str(self.nodeID)
			exec(q + " = self.q_obj.create_queue(" + "'" + str(q) + "'" + ")")
			exec("self.queue = self.q_obj.get_from_repository(" + "'" +"q_" + str(self.nodeID)+ "'" + ")")
			seed = self.create_random_seed()
			init_route_packet = InitialRoutePacket(self.nodeID, seed)
			qname_index = 0
			for q in self.q_list:
				deep_obj_copy = deepcopy(init_route_packet)
				deep_obj_copy.packet_id = self.generate_uuid()
				status = self.q_obj.put_to_queue(q,deep_obj_copy)
				temp_node_name = self.neighbor_qname_list[qname_index].split('_')[1]
				log_msg= self.packet_logger_message(deep_obj_copy.packet_id,temp_node_name , 'SENT', 'INIT_ROUTE')
				self.packet_logger.write_log(log_msg)
				qname_index = qname_index+1
		
		else:
			exec("self.queue = self.q_obj.get_from_repository(" + "'" +"q_" + str(self.nodeID)+ "'" + ")")
			exec("q_size = self.q_obj.get_qsize (" + "'" + self.queue + "'" + ")")
			q_counter = 0

			for i in range(q_size):
				exec ("init_route_packet_" +str(self.nodeID)+ "_"+ str(q_counter) + " =  self.q_obj.get_from_queue (" + repr(self.queue) + ")")
				seed = self.create_random_seed()
				exec ("pkt_id = init_route_packet_" +str(self.nodeID)+ "_"+ str(q_counter) + ".packet_id")
				log_msg= self.packet_logger_message(pkt_id, "r", 'RCVD', 'INIT_ROUTE')
				self.packet_logger.write_log(log_msg)
				exec ("disp_pkt = init_route_packet_" + str(self.nodeID) + "_" + str(q_counter) + ".get_packet()")
				exec ("init_route_packet_" + str(self.nodeID) + "_" + str(q_counter) + ".add_id_seed(self.nodeID, seed)" )
				deep_copy_dict_name = "deep_copy_dict_" + str(self.nodeID)
				exec (deep_copy_dict_name + " = {}")
				deep_copy_key = 0
				for q in self.q_list:
					#deep_obj_copy = deepcopy(init_route_packet)
					exec ( deep_copy_dict_name +"[deep_copy_key] = deepcopy(init_route_packet_" + str(self.nodeID)+ "_" + str(q_counter) + ")")
					exec (deep_copy_dict_name + "[deep_copy_key].packet_id = self.generate_uuid()")
					exec ("pkt_id = " + deep_copy_dict_name + "[deep_copy_key].packet_id")
					exec( "status = self.q_obj.put_to_queue(q," +deep_copy_dict_name + "[deep_copy_key])")
					temp_node_name = self.neighbor_qname_list[deep_copy_key].split('_')[1]
					log_msg= self.packet_logger_message(pkt_id, temp_node_name , 'SENT', 'INIT_ROUTE')
					self.packet_logger.write_log(log_msg)
					deep_copy_key = deep_copy_key + 1
				q_counter = q_counter + 1

		self.dissipation_event.wait()
		exec("q_size_for_pattern = self.q_obj.get_qsize (" + "'" + self.queue + "'" + ")")
		self.pattern_packet = self.q_obj.get_from_queue(self.queue)
		pkt_id = self.pattern_packet.packet_id
		log_msg= self.packet_logger_message(pkt_id, "r" , 'RCVD', 'PATTERN')
		self.packet_logger.write_log(log_msg)

		if self.beginner:
			self.dissipation_event.clear()
		self.pattern = self.pattern_packet.get_this_pattern()
		self.next_pattern = self.pattern_packet.get_next_pattern()
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
				retrieved_get = self.pend_on_queue(q_, timeout,sleeptime)
				return retrieved_get
			else:
				retrieved_get = q_.get_nowait()
				pkt_to_forward = retrieved_get
				if pkt_to_forward is not None:
					if isinstance(pkt_to_forward, DataPacket):
						if pkt_to_forward.packet_id:
							pkt_id = pkt_to_forward.packet_id
						else:
							pkt_id = self.generate_uuid()
						log_msg= self.packet_logger_message(pkt_id, "r" , 'RCVD', 'DATA')
						self.packet_logger.write_log(log_msg)

						if not pkt_to_forward.get_pattern():
							pkt_to_forward.pattern.append(self.pattern)
						if pkt_to_forward.get_pattern()[len(pkt_to_forward.get_pattern())-1] == self.pattern:
							forward_counter = 1
							for q in self.q_list:
								exec("deep_copy_" + str(forward_counter) + " = deepcopy(pkt_to_forward) ")
								exec("deep_copy_" + str(forward_counter) + ".pattern.append(self.next_pattern)")
								exec("deep_copy_" + str(forward_counter) + ".packet_id= self.generate_uuid()")
								exec("pkt_id = deep_copy_" + str(forward_counter) + ".packet_id")
								exec( "status = self.q_obj.put_to_queue(q, deep_copy_" + str(forward_counter) + ")" )
								#get packet id and add packet sent debug
								temp_node_name =  str(self.neighbor_qname_list[forward_counter-1]).split('_')[1]
								log_msg= self.packet_logger_message(pkt_id, temp_node_name , 'SENT', 'DATA')
								self.packet_logger.write_log(log_msg)
								forward_counter = forward_counter + 1
				retrieved_get = self.pend_on_queue(self.queue, self.pend_on_queue_time)
		return retrieved_get
			
					
	
	def create_random_seed(self):
		from random import randrange
		return randrange(255)
		

	def create_neighbor_queues(self):
		qname_list = []
		for neighbor in self.neighbor_dict[self.nodeID]:
			qname = "q_" + str(neighbor)
			qname_list.append(qname)
		queue_object_list = []
		for q in qname_list:
			if self.q_obj.check_if_created(q):
				exec(q + " = self.q_obj.get_object_by_name(" + "'" + str(q) + "'" + ")")
			else:
				exec(q + " = self.q_obj.create_queue(" + "'" + str(q) + "'" + ")")
			exec("queue_object_list.append(" + str(q) + ")")
		return queue_object_list, qname_list


	def packet_logger_message(self, pktid, to_, sent_or_received, pkt_type):
		message = ""
		if sent_or_received == self.sent_flag:
			message = pktid + "  " + pkt_type + "  " + str(self.nodeID) + "  " +str(to_) + "  " + sent_or_received +  "\n"
		elif sent_or_received == self.received_flag:
			message = pktid + "  " + pkt_type + "  " + str(to_) + "  " + str(self.nodeID) + "  "  + sent_or_received +	"\n"
		return message

			

	def generate_uuid(self):
		str_uuid_full = str(uuid.uuid4()).split('-')
		pkt_id = str_uuid_full[len(str_uuid_full)-1]
		return pkt_id
