import sys

class PatternPacket(object):

	def __init__(self, this_pattern, next_pattern):
		self.this_pattern = this_pattern
		self.next_pattern = next_pattern
		self.packet_id = ''

	def get_this_pattern(self):
		return self.this_pattern

	def get_next_pattern(self):
		return self.next_pattern

	def get_packet_id(self):
		return self.packet_id
