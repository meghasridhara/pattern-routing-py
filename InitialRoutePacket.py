import sys

class InitialRoutePacket(object):
	id_seed_list = []

	def __init__(self, nodeID, seed):
		self.id_seed_list = [(nodeID, seed)]
		self.packet_id = ''

	def add_id_seed(self, nid, rseed):
		self.id_seed_entry= (nid,rseed)
		self.id_seed_list.append(self.id_seed_entry)
		
	def get_packet(self):
		return self.id_seed_list		

	def get_packet_id(self):
		return self.packet_id
