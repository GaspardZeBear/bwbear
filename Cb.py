import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
from Outer import *
from DFFormatter import *

percentiles=[.50,.95,.99]
pd.options.display.float_format = '{:.0f}'.format
timeGroupby='ts1m'
timeFormat='%H-%M'
HIGHRESPONSETIME=20000 

#--------------------------------------------------------------------------------------
def graphAggregated(aggr,dgAggr,title,color='blue') :
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))
  fig.autofmt_xdate()
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter(timeFormat))
  dgAggr.plot(title=aggr + " " + title,color=color,rot=45,ax=ax,grid=True)
  f=title + aggr + '.png'
  plt.savefig(f)
  plt.close()
  OUT.image(f,aggr + " " +title)

#--------------------------------------------------------------------------------------
def graphBasicsNew(id,dgbase,dgList) :
  logging.warning("graphBasics aggr=" + id)
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))
  fig.autofmt_xdate()
  logging.warning("graphBasics setting ax")
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter(timeFormat))
  ax.set_ylabel('Time ms', color='black')
  title=id
  dfall.plot(rot=45,ax=ax,grid=True,linewidth=0)
  for dg in dgList : 
    title=title +  dg['aggr']
    dg['dgaggr'].plot(title=dg['aggr'],rot=45,ax=ax,grid=True,color=dg['color'],label=dg['aggr'],linewidth=1)
    ax.set_ylim(ymin=0)
  logging.warning("graphBasics setting axtwin")
  axtwin=ax.twinx()
  axtwin.set_ylabel('Count', color='lightgrey')
  dfCount=dgbase.count().reset_index()
  dfm=pd.merge_ordered(dfall,dfCount,left_on='ts1m',right_on='ts1m',how='outer')
  dfm = dfm.set_index(timeGroupby)
  dfm.drop('StartTime',axis=1,inplace=True)
  dfm.fillna(value=0,inplace=True)

  dgbase.count().plot(ax=axtwin,style='o')
  dgbase.count().plot(ax=axtwin,color='lightgrey',linestyle='-.')
  dfm.plot(ax=axtwin,color='lightgrey',linestyle='--',label='Count')
  axtwin.set_ylim(ymin=0)
  f=title.translate(None,' /.,:;\[]()-') + '.png'
  plt.savefig(f)
  plt.close()
  OUT.image(f,title)



#--------------------------------------------------------------------------------------
def graphAggregatedBar(aggr,dgAggr,title,color='blue') :
  logging.warning(dgAggr)
  plt.figure(figsize=(10,8))
  fig, ax=plt.subplots(figsize=(16,4))

  dgAggr.plot(kind='barh',title=aggr + " " + title,color=color,ax=ax,grid=True)
  f=title + aggr + '.png'
  plt.savefig(f)
  plt.close()
  OUT.image(f,title)



#--------------------------------------------------------------------------------------
def myPlotBarResponseTime(datas,title,color='blue') :
  if datas.empty :
    return
  rtime=datas['ResponseTime']
  plt.figure(figsize=(17,4))
  rtime.plot.bar(title=title,rot=45,color=color)
  f=title + '.png'
  plt.savefig(f)
  OUT.image(f,title)

#--------------------------------------------------------------------------------------
def myGraphs(datas,title,color='blue') :
  if datas.empty :
    return
  dg=datas.groupby(timeGroupby)['ResponseTime']
  graphBasicsNew(title + 'Mean, Q50 .. : ', dg, [ 
    { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
    { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'grey'},
    ])
  graphBasicsNew(title + 'Max, Q99, Q95 .. : ', dg, [ 
    { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
    { 'aggr' : 'Q99', 'dgaggr' : dg.quantile(0.99), 'color' : 'black'},
    { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'grey'},
    ])
  

#--------------------------------------------------------------------------------------
def myGraphsErrors(datas,title,color='red') :
  if datas.empty :
    return
  dg=datas.groupby(timeGroupby)['Error']
  #logging.warning(dg.sum())
  graphAggregated('Sum', dg.sum() ,title, color)


#--------------------------------------------------------------------------------------
def groupByDescribe(datas,grps) :
  if datas.empty :
    return
  dg=datas.groupby(grps)['ResponseTime']
  OUT.out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=percentiles))

#--------------------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING)
OUT=OutputHtml()
#OUT=OutputTty()
OUT.open()
rawDatas=DFFormatter(sys.argv[1],OUT).getDf()
logging.debug(rawDatas)
rawDatas=rawDatas[rawDatas.PurePath.str.contains("assets")==False]

OUT.h2("Analyzing transaction in Error ")
myGraphsErrors(rawDatas,'All Errors over time')
groupByDescribe(rawDatas,["ErrorState"])
dfKO=rawDatas[ ( rawDatas['ErrorState'] != 'OK') ]
groupByDescribe(dfKO,["Agent"])
groupByDescribe(dfKO,["PurePath"])
#myGraphs(dfKO,'All Errors')

OUT.h2("Analyzing transactions in status OK ")
dfOK=rawDatas[ ( rawDatas['ErrorState'] == 'OK' ) ]
groupByDescribe(dfOK,["Agent"])
groupByDescribe(dfOK,["PurePath"])

dfall=pd.DataFrame(dfOK.groupby(timeGroupby)['StartTime'].count().apply(lambda x: 0))
myGraphs(dfOK,'All OK')
for pp in dfOK['PurePath'].unique() :
  myGraphs(dfOK[dfOK['PurePath'] == pp], pp)
#myGraphs(dfOK[ ( dfOK['PurePath'] == '/cos/fr/rxp/view.exportxls')] , 'xxx')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'RemiseTab') ] ,'RemiseTab')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'Result5') ] ,'Result5')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchRemisesDate') ] ,'SearchRemisesDate')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDate') ] ,'SearchTransactionsDate')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDateScheme') ] ,'SearchTransactionsDateScheme')
#myGraphs(dfOK[ ( dfOK['PurePath'] == 'TransactionDetail') ] ,'TransactionDetail')

OUT.h2("Analyzing transactions with high response time")
groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > 5000 ) ],["PurePath"])
OUT.out("Samples OK having high resp time ",dfOK[ ( dfOK['ResponseTime'] > HIGHRESPONSETIME ) ])

OUT.h2("Detail of transactions in error state")
OUT.out("Samples KO failed ",dfKO)
#OUT.out("Rawdatas detail",dfOK)

