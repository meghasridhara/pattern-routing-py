import Queue
from threading import Lock


qlock = Lock()
class Queues(object):

	def __init__(self):
		self.q_repository = {}

	def add_to_repository(self, new_q_entry):
		self.q_repository.update(new_q_entry)
		return	
		
	def get_from_repository (self, qname):
		qlock.acquire()
		retqname = None
		try:
			if qname in self.q_repository.keys():
				retqname = qname
		finally:
			qlock.release()
		return retqname
	
	def create_queue(self, qname):
		qlock.acquire()
		return_queue = None
		try:
			qname_key = str(qname)
			qname_value = Queue.Queue()
			q_entry = {qname_key : qname_value}	
			self.add_to_repository(q_entry)
			return_queue = qname_value
		finally:
			qlock.release()
		return return_queue

	def put_to_queue(self, qname, put_this):
		qname.put(put_this)
		return True

	def get_from_queue(self, qname):
		q_value = self.q_repository[qname].get()
		return q_value

	def get_qsize(self,qname):
		qlock.acquire()
		try:
			queue_size = self.q_repository[qname].qsize()
		finally:
			qlock.release()
		return queue_size

	def get_qname_by_object(self, queue_object):
		for q_tup in self.q_repository.items():
			if queue_object == q_tup[1]:
				return q_tup[0] 

	def get_object_by_name (self, qname):
		qlock.acquire()
		return_q_obj = None
		try:
			if qname in self.q_repository.keys():
				return_q_obj = self.q_repository[qname]
		finally:
			qlock.release()
		return return_q_obj
			

	def check_if_created(self, qname):
		return_val = False
		qlock.acquire()
		try:
			if qname in self.q_repository.keys():
				return_val = True
		finally:
			qlock.release()
		return return_val		

	def get_q_repository(self):
		q_rep = {}
		return self.q_repository
