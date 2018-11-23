import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from Outer import *

#ErrorState;PurePath;ResponseTime;Agent;Application;StartTime
#OK;/casino/fr/transaction/list;11236.98926;11321;centralreport-casino-vindemia.aw.atos.net;2018-11-14 05:59:57;
#OK;/casino/fr/transaction/list;9426.301758;11321;centralreport-casino-vindemia.aw.atos.net;2018-11-14 06:00:00;
#OK;/casino/;400.1700439;11321;centralreport-casino-hyper-super.aw.atos.net;2018-11-14 06:00:01;

percentiles=[.50,.95,.99]
pd.options.display.float_format = '{:.0f}'.format
PP={
      "Go to page result 5" : "Result5",
      "Go to remise detail" : "RemiseDetail",
      "Go to remises tab" : "RemiseTab",
      "Go to transaction detail" : "TransactionDetail",
      "Search remises on Date" : "SearchRemisesDate",
      "Search transactions on Date" : "SearchTransactionsDate",
      "Search transactions on Date & paymentScheme" : "SearchTransactionsDateScheme",
}

#--------------------------------------------------------------------------------------
def graphErrors(datas,title) :
  #datas['ts']=datas['StartTime'].apply(lambda x: x[0].timestamp(), axis=1).astype(int)
  stime=datas
  stime['StartTime']=pd.to_datetime(stime['StartTime'],infer_datetime_format=True)
  print(stime.head())
  stime.set_index('StartTime',inplace=True)
  print(stime.head())
  stime.index = stime.index.floor('1T')
  print(stime.head())
  plt.figure(figsize=(16,4))
  print(stime.groupby('StartTime')['ErrorState'].count())
  stime.groupby('StartTime')['ErrorState'].count().plot.bar(title=title,rot=0,color='red')
  f=title + '.png'
  plt.savefig(f)
  OUT.image(f,title)




#--------------------------------------------------------------------------------------
def renamePP(u) :
  if ( u in PP ) :
    return(PP[u])
  return(u)

#--------------------------------------------------------------------------------------
def getRawdatas(f='cb.csv') :
  pd.set_option("display.max_rows",None)
  #pd.set_option("display.max_rows",10)
  rawdatas=pd.read_csv(f,sep=';')
  OUT.h1("Analyzing file " + f)
  OUT.h2("Raw datas")
  OUT.out("File HEAD",rawdatas.head())
  OUT.out("File TAIL",rawdatas.tail())
  rawdatas.drop (
      ["Breakdown","Size","Top Findings","Duration [ms]"],
      inplace=True,axis=1
  )   
  rawdatas.rename ({
      "Error State" : "ErrorState",
      "PurePath" : "PurePath",
      "Response Time [ms]" : "ResponseTime",
      "Start Time" : "StartTime"
  },inplace=True,axis=1)
  rawdatas['PurePath']=rawdatas['PurePath'].map(renamePP)
  OUT.out("File header and PP name reformatted",rawdatas.head())
  OUT.out("File statistics",rawdatas.describe(percentiles=percentiles))
  return(rawdatas)

#--------------------------------------------------------------------------------------
def myPlotBarResponseTime(datas,title) :
  if datas.empty :
    return 
  rtime=datas['ResponseTime']
  plt.figure(figsize=(17,4))
  rtime.plot.bar(title=title,rot=0,color='blue')
  f=title + '.png'
  plt.savefig(f)
  OUT.image(f,title)

#--------------------------------------------------------------------------------------
def XgraphErrors(datas,title) :
  #datas['ts']=datas['StartTime'].apply(lambda x: x[0].timestamp(), axis=1).astype(int)
  stime=datas
  stime['x']=pd.to_datetime(stime['StartTime'],infer_datetime_format=True)
  print(stime.head())
  stime.set_index('x',inplace=True)
  print(stime.head())
  stime.index = stime.index.floor('1H')
  plt.figure(figsize=(16,4))
  stime.plot.hist(title=title,rot=0,color='red')
  f=title + '.png'
  plt.savefig(f)
  OUT.image(f,title)


#--------------------------------------------------------------------------------------
def groupByDescribe(datas,grps) :
  if datas.empty :
    return 
  dg=datas.groupby(grps)
  OUT.out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=percentiles))


#--------------------------------------------------------------------------------------
OUT=OutputHtml()
#OUT=OutputTty()
OUT.open()
rawDatas=getRawdatas(sys.argv[1])

OUT.h2("Analyzing transaction in Error ")
groupByDescribe(rawDatas,["ErrorState"])
dfKO=rawDatas[ ( rawDatas['ErrorState'] != 'OK') ]
groupByDescribe(dfKO,["Agent"])
groupByDescribe(dfKO,["PurePath"])
graphErrors(dfKO,'Errors')

sys.exit()
OUT.h2("Analyzing transactions in status OK ")
dfOK=rawDatas[ ( rawDatas['ErrorState'] == 'OK' ) ]
groupByDescribe(dfOK,["Agent"])
groupByDescribe(dfOK,["PurePath"])
myPlotBarResponseTime(dfOK,'All')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseTab') ] ,'RemiseTab')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'Result5') ] ,'Result5')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchRemisesDate') ] ,'SearchRemisesDate')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDate') ] ,'SearchTransactionsDate')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDateScheme') ] ,'SearchTransactionsDateScheme')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'TransactionDetail') ] ,'TransactionDetail')

OUT.h2("Analyzing transactions with high response time")
groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > 5000 ) ],["PurePath"])
OUT.out("Samples OK having resp time 5 secondes ",dfOK[ ( dfOK['ResponseTime'] > 5000 ) ])

OUT.h2("Detail of transactions in error state")
OUT.out("Samples KO failed ",dfKO)
#OUT.out("Rawdatas detail",dfOK)
