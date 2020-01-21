import re
import sys
from jinja2 import Environment, FileSystemLoader
import tqdm

maxdate = None
mindate = None
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
   	 #print(splitarray)
   	 if len(splitarray)>1:
   		 #self._ip = splitarray[0]
   		 for t in ParserLineLog.LOGTYPE:
   			 if splitarray[0].find(t) != -1:
   				 self._type = t
   				 if self._type == "LOG":
   					 self._parseSql(self._line)
    @property
    def tablename(self):    	 
   	 return self._tablename
  	 
 	# a setter function
    @tablename.setter
    def tablename(self, t):
   	 if "pg_" not in t:
   		 self._tablename = t.replace("public_","")

    def _parseSql(self, line):
   	 #print("parseSql %s " % line)
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

   			 if self._sqloperation.upper() =="PREPARE":
   				 if line.find("SELECT") != -1:
   					 self._sqloperation = "SELECT"
   					 ta = re.split("PREPARE ([a-zA-Z0-9_]+) AS", line, flags=re.IGNORECASE)
   					 self.parseSelect(ta[2])
   					 #arraytmp[1]= ta[2]

   			 if self._sqloperation.upper() =="SELECT":
   				 self.parseSelect(arraytmp[1])

   			 if self._sqloperation.upper() =="INSERT":
   				 ta = re.split("INTO", arraytmp[1], flags=re.IGNORECASE)
   				 self.tablename = ta[1].split(" ")[1].split("(")[0]
   				 
   			 if self._sqloperation.upper() =="UPDATE":
   				 ta = re.split("UPDATE ", arraytmp[1], flags=re.IGNORECASE)
   				 self.tablename = ta[1].split(" ")[0].replace(";", "").replace("\n", "")
   			 
   			 #print("%s %s" % ( self._sqloperation,self._tablename))

    def parseSelect(self, line):
   	 ta = re.split("FROM", line, flags=re.IGNORECASE)   				 
   	 if len(ta)>1:
   		 if len(ta[1].split(" "))>1:
   			 self.tablename = ta[1].split(" ")[1]    .replace(";", "").replace("\n", "")

    def _parseDate(self):
   	 # Parse self._line [2007-08-31 19:22:21.469 ADT] ...
   	 # and remove the date of _line
   	 datestr = self._line.split("[")
   	 if len(datestr)>1:
                    	# dateparser takes a long time to process
   		 #self._date = dateparser.parse(datestr[0].replace("[",""))
   		 #print(self._date)
   		 self._line = ''.join(datestr[1:])
   		 #print(self._line)


countTable= {}
countTableInsert= {}
countTableUpdate = {}
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
#with open('log.txt', 'r') as reader:
num_lines = sum(1 for line in open(sys.argv[1]))
tq = tqdm.tqdm(total=num_lines, unit_scale=True)
n = 0
with open(sys.argv[1], 'r') as reader:
    for line in reader:   	 
   	 n = n + 1
   	 tq.update(1)
   	 p = ParserLineLog(line)   	 
   	 if p._type == "LOG":
                	if p._sqloperation == "SELECT":
                    	if p._tablename not in countTable:
                        	countTable[p._tablename ]= 1
                    	else:
                        	countTable[p._tablename]= countTable[p._tablename]+ 1
                       	 
                	if p._sqloperation =="INSERT":
                    	if p._tablename not in countTableInsert:
                        	countTableInsert[p._tablename ]= 1
                    	else:
                        	countTableInsert[p._tablename]= countTableInsert[p._tablename]+ 1
                       	 
                	if p._sqloperation =="UPDATE":
                    	if p._tablename not in countTableUpdate:
                        	countTableUpdate[p._tablename ]= 1
                    	else:
                        	countTableUpdate[p._tablename]= countTableUpdate[p._tablename]+ 1               	 
                   	 
   	 
   	 #print(n)
#print("END")   	 
tq.close()   	 
           	 
template = env.get_template('barchart.html')
output = template.render(table=countTable,title="SELECT request", tableinsert = countTableInsert,  tableupdate = countTableUpdate)
print(output)
