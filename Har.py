import json
import datetime
import sys

class Parser :

    def __init__(self,har):
        with open(har, "r") as read_file:
           data = json.load(read_file)

        log_data = data['log']
        self.data = log_data
        self.entries = self.data['entries']
        count=1
        self.printHeader()
        for e in self.entries :
            print(self.parseEntry(e)[:-1])
            count +=1

    def accum(self,base,val,quote='') :
        if base :
          return(quote + str(base[val]) + quote + ';')
        else :
          return(quote + str(val) + quote + ';')

    def getUrl(self,url) : 
        if url.find('?') > 0 :
          return(url[:url.find('?')])
        else :
          return(url)
        
#--------------------------------------------------------------------------------------------------------------
class Parser2Pan(Parser) :

    def printHeader(self) :
        print("ErrorState;PurePath;ResponseTime;Agent;Application;StartTime;StartTimeStr;ts1m;ts10m;ts1h;Error")


    def parseEntry(self,e) :
        s =''
        s += self.accum(None,'OK')
        s += self.accum(None,self.getUrl(e['request']['url']),'"')
        s += self.accum(e,'time')
        s += self.accum(None,'_Agent')
        s += self.accum(None,'_Application')
        #s += self.accum(e['response'],'status')
        #s += self.accum(None,e['startedDateTime'][0:23].replace('T',' '))
        #s += self.accum(None,e['startedDateTime'][0:23].replace('T',' '))
        #s += self.accum(None,e['startedDateTime'][0:19].replace('T',' ') + '.000')
        #s += self.accum(None,e['startedDateTime'][0:18].replace('T',' ') + '0.000')
        #s += self.accum(None,e['startedDateTime'][0:14].replace('T',' ') + '00:00.000')
        s += self.accum(None,e['startedDateTime'][0:19].replace('T',' '))
        s += self.accum(None,e['startedDateTime'][0:19].replace('T',' '))
        s += self.accum(None,e['startedDateTime'][0:17].replace('T',' ') + '00' )
        s += self.accum(None,e['startedDateTime'][0:15].replace('T',' ') + '0:00')
        s += self.accum(None,e['startedDateTime'][0:14].replace('T',' ') + '00:00')

        s += self.accum(None,'0')
        #s += self.accum(e['response'],'bodySize')
        return(s)

#--------------------------------------------------------------------------------------------------------------
class Parser2Csv(Parser) :

    def printHeader(self) :
        print("StartTime;Status;ResponseTime;PurePath;HeadersSize;BodySize;ConnectTime;SSLTime;SendTime;ReceiveTime;")

    def parseEntry(self,e) :
        s =''
        s += self.accum(None,e['startedDateTime'].replace('T',' ')[:23])
        s += self.accum(e['response'],'status')
        s += self.accum(e,'time')
        s += self.accum(None,self.getUrl(e['request']['url']),'"')
        s += self.accum(e['response'],'headersSize')
        s += self.accum(e['response'],'bodySize')
        s += self.accum(e['timings'],'connect')
        s += self.accum(e['timings'],'ssl')
        s += self.accum(e['timings'],'send')
        s += self.accum(e['timings'],'receive')
        return(s)

#--------------------------------------------------------------------------------------------------------------
if __name__ == "__main__" : 
    if sys.argv[2] == 'pan' :
      p=Parser2Pan(sys.argv[1])
    elif sys.argv[2] == 'csv' :
      p=Parser2Csv(sys.argv[1])



