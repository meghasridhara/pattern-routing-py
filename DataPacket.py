import sys

class DataPacket(object):
	
	def __init__(self, data_, pattern_=[]):
		self.data = data_
		self.pattern = pattern_
		self.packet_id = ''

	def get_data(self):
		return self.data

	def get_pattern(self):
		return self.pattern
	
	def get_packet_id(self):
		return self.packet_id

	


                            
