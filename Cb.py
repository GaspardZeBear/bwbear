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
YLIM=10000

#--------------------------------------------------------------------------------------
def graphAggregated(aggr,dgAggr,title,color='blue') :
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))
  #plt.ylim(0,YLIM)
  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter(timeFormat))
  dgAggr.plot(title=aggr + " " + title,color=color,rot=45,ax=ax,grid=True)
  f=title + aggr + '.png'
  plt.savefig(f)
  plt.close()
  OUT.image(f,aggr + " " +title)

#--------------------------------------------------------------------------------------
def graphBasics(aggr,dg,title,color='blue') :
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))
  #plt.ylim(0,YLIM)
  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter(timeFormat))
  dg.mean().plot(title=aggr + " mean " + title,rot=45,ax=ax,grid=True,color='black',label='Mean',linewidth=2)
  dg.quantile(0.5).plot(title=aggr + " median " + title,rot=45,ax=ax,grid=True,color='grey',label='Median',linestyle='--')
  dg.quantile(0.95).plot(title=aggr + " 0.95 " + title,rot=45,ax=ax,grid=True,color='lightgrey',label='Q95',linestyle='-.')
  f=title + aggr + '.png'
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
  graphAggregated('Count', dg.count() ,title, color)
  graphAggregated('Mean', dg.mean(), title, color)
  #graphAggregated('Q50', dg.quantile(0.50), title, color)
  #graphAggregated('Q95', dg.quantile(0.95), title, color)
  graphAggregated('Max', dg.max(), title, color)
  graphBasics('Mean, median -- , Q95 .. : ', dg, title, color)

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
  dg=datas.groupby(grps)
  OUT.out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=percentiles))
  #graphAggregatedBar('Count', dg.count(), str(grps), 'green')
  #graphAggregatedBar('Mean', dg.mean(), str(grps), 'green')

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
myGraphs(dfOK,'All OK')


#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseTab') ] ,'RemiseTab')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'RemiseTab') ] ,'RemiseTab')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'Result5') ] ,'Result5')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'Result5') ] ,'Result5')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchRemisesDate') ] ,'SearchRemisesDate')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchRemisesDate') ] ,'SearchRemisesDate')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDate') ] ,'SearchTransactionsDate')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDate') ] ,'SearchTransactionsDate')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDateScheme') ] ,'SearchTransactionsDateScheme')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDateScheme') ] ,'SearchTransactionsDateScheme')
#myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'TransactionDetail') ] ,'TransactionDetail')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'TransactionDetail') ] ,'TransactionDetail')

OUT.h2("Analyzing transactions with high response time")
groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > 5000 ) ],["PurePath"])
OUT.out("Samples OK having high resp time ",dfOK[ ( dfOK['ResponseTime'] > 10000 ) ])

OUT.h2("Detail of transactions in error state")
OUT.out("Samples KO failed ",dfKO)
#OUT.out("Rawdatas detail",dfOK)

