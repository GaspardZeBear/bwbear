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
timeGroupby='ts10m'
#--------------------------------------------------------------------------------------
def graphAggregatedCount(datas,title,color='blue') :
  logging.warning('Entering graphAggregatedCount')
  logging.warning(datas.head())
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))

  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
  datas.groupby(timeGroupby)['ResponseTime'].count().plot(title='Count ' + title,color=color,rot=45,ax=ax)
  f=title + 'Count.png'
  plt.savefig(f)
  OUT.image(f,title) 

#--------------------------------------------------------------------------------------
def graphAggregatedMean(datas,title,color='blue') :
  logging.warning('Entering graphAggregatedMean')
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))

  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
  datas.groupby(timeGroupby)['ResponseTime'].mean().plot(title='Mean ' + title,color=color,rot=45,ax=ax)
  f=title + 'Mean.png'
  plt.savefig(f)
  OUT.image(f,title)

#--------------------------------------------------------------------------------------
def graphAggregatedMax(datas,title,color='blue') :
  logging.warning('Entering graphAggregatedMax')
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))

  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
  datas.groupby(timeGroupby)['ResponseTime'].max().plot(title='Max ' + title,color=color,rot=45,ax=ax)
  f=title + 'Max.png'
  plt.savefig(f)
  OUT.image(f,title)


#--------------------------------------------------------------------------------------
def graphAggregatedQuantile95(datas,title,color='blue') :
  logging.warning('Entering graphAggregatedMean')
  plt.figure(figsize=(16,4))
  fig, ax=plt.subplots(figsize=(16,4))

  fig.autofmt_xdate()
  # use a more precise date string for the x axis locations in the
  # toolbar
  ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
  ax.set_title('fig.autofmt_xdate fixes the labels')
  ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
  datas.groupby(timeGroupby)['ResponseTime'].quantile(0.95).plot(title='95 ' + title,color=color,rot=45,ax=ax)
  f=title + '95.png'
  plt.savefig(f)
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
  graphAggregatedCount(datas, title, color)
  graphAggregatedMean(datas, title, color)
  graphAggregatedQuantile95(datas, title, color)
  graphAggregatedMax(datas, title, color)


#--------------------------------------------------------------------------------------
def groupByDescribe(datas,grps) :
  if datas.empty :
    return
  dg=datas.groupby(grps)
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
groupByDescribe(rawDatas,["ErrorState"])
dfKO=rawDatas[ ( rawDatas['ErrorState'] != 'OK') ]
groupByDescribe(dfKO,["Agent"])
groupByDescribe(dfKO,["PurePath"])
myGraphs(dfKO,'All Errors')

OUT.h2("Analyzing transactions in status OK ")
dfOK=rawDatas[ ( rawDatas['ErrorState'] == 'OK' ) ]
groupByDescribe(dfOK,["Agent"])
groupByDescribe(dfOK,["PurePath"])
myGraphs(dfOK,'All OK')


myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail response time')
myGraphs(dfOK[ ( dfOK['PurePath'] == 'RemiseDetail') ] ,'RemiseDetail response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'RemiseTab') ] ,'RemiseTab response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'Result5') ] ,'Result5 response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchRemisesDate') ] ,'SearchRemisesDate response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDate') ] ,'SearchTransactionsDate response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'SearchTransactionsDateScheme') ] ,'SearchTransactionsDateScheme response time')
myPlotBarResponseTime(dfOK[ ( dfOK['PurePath'] == 'TransactionDetail') ] ,'TransactionDetail response time')

OUT.h2("Analyzing transactions with high response time")
groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > 5000 ) ],["PurePath"])
OUT.out("Samples OK having resp time 5 secondes ",dfOK[ ( dfOK['ResponseTime'] > 5000 ) ])

OUT.h2("Detail of transactions in error state")
OUT.out("Samples KO failed ",dfKO)
#OUT.out("Rawdatas detail",dfOK)

