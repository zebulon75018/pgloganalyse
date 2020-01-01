import dateparser
import re
	
class ParserLineLog:
	LOGTYPE = ["ERROR","LOG","FATAL","UNKNOWED"]
	def __init__(self, line):
	
		self._ip = None
		self._date = None
		self._line = line
		self._type = "UNKNOWED"
		self._sqloperation = "UNKNOWED"
		self._tablename = ""
		# Parse Date ...
		self._parseDate()
	
		splitarray = self._line.split(":")

		if len(splitarray)>1:
			self._ip = splitarray[0]
			for t in ParserLineLog.LOGTYPE: 
				if splitarray[1].find(t) != -1:
					self._type = t 
					if self._type == "LOG":
						self._parseSql(self._line)
	
	def _parseSql(self, line):
		# parse the sql ....
		if line.find('statement:') != -1:
			arraytmp = line.split("statement:")
			if len(arraytmp)>1:
				operande = arraytmp[1].split(" ")
				# operande could be ['', 'SELECT', 'id', 'FROM', 'location', 'WHERE', 'name',
				# the first one can be empty .. so an hugly test.
				if len(operande[0])>2:
					self._sqloperation =operande[0]
				else:
					self._sqloperation =operande[1]
				
				if self._sqloperation.upper() =="SELECT":
					ta = re.split("FROM", arraytmp[1], flags=re.IGNORECASE)			
					self._tablename = ta[1].split(" ")[1]	
				if self._sqloperation.upper() =="INSERT":
					ta = re.split("INTO", arraytmp[1], flags=re.IGNORECASE)
					self._tablename = ta[1].split(" ")[1].split("(")[0]
					
				if self._sqloperation.upper() =="UPDATE":
					ta = re.split("UPDATE ", arraytmp[1], flags=re.IGNORECASE)
					self._tablename = ta[1].split(" ")[0]
				
				print(self._tablename)
					
	def _parseDate(self):
		# Parse self._line [2007-08-31 19:22:21.469 ADT] ...
		# and remove the date of _line
		datestr = self._line.split("]")
		if len(datestr)>1:
			self._date = dateparser.parse(datestr[0].replace("[",""))
			self._line = ''.join(datestr[1:])


with open('log.txt', 'r') as reader:
	for line in reader:
		p = ParserLineLog(line)
		#print(line)
		