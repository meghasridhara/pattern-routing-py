import sys
from threading import Lock

log_lock = Lock()

class LogRecord(object):
	def __init__(self, fname):
		self.fname=fname


	def write_log(self, log_message):
		log_lock.acquire()
		status = False
		try:
			target = open(self.fname, 'a')	
			target.write(log_message)
			target.close()
			log_lock.release()
		except Exception as e:
			print ("Problem writing file!")
		return 

	def truncate_log(self):
		log_lock.acquire()
		try:
			target = open(self.fname, 'w')
			target.truncate()
			log_lock.release()
		except Exception as e:
			print "Problem truncating file"
		return
