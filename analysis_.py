import sys



analysis_filename = "packetlogger.txt"



def getline(filename):
	for line in open(filename):
            yield line 


def get_count(filename):
	sendcount = 0 
	rcvdcount = 0
	for line_ in getline(filename):
		if 'DATA' in line_:
			if 'SENT' in line_:
				sendcount = sendcount+1
			if 'RCVD' in line_:
				rcvdcount = rcvdcount+1
	return float(sendcount),float(rcvdcount)

def do_analysis(sendcount,rcvdcount):
	ratio = 0
	if sendcount>rcvdcount:
		ratio = rcvdcount/sendcount
	else:
		ratio = sendcount/rcvdcount
	print "The packet delivary Ratio is " + str(ratio)
	print "Percentage of packets delivered " + str(ratio*100) + "%"
	return ratio


if __name__ == '__main__':
	send, rcv = get_count(analysis_filename)
	do_analysis(send, rcv)
	
	
	
