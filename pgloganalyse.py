import dateparser

class PaserLineLog:
	def __init__(self, line):
		# Parse Date ...
		datestr = line.split("]")
		if len(datestr)>1:
			print(datestr[0].replace("[",""))
			print(dateparser.parse(datestr[0].replace("[","")))
	

with open('log.txt', 'r') as reader:
	for line in reader:
		p = PaserLineLog(line)
		print(line)
		