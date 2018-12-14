import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
from Outer import *
from DFFormatter import *
from Param import *
import click

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
    dg['dgaggr'].plot(title=dg['aggr'],rot=45,ax=ax,grid=True,color=dg['color'],legend=True,label=dg['aggr'],linewidth=1)
    ax.set_ylim(ymin=0)
  logging.warning("graphBasics setting axtwin")
  axtwin=ax.twinx()
  axtwin.set_ylabel('Count', color='lightgrey')
  dfCount=dgbase.count().reset_index()
  dfm=pd.merge_ordered(dfall,dfCount,left_on='ts1m',right_on='ts1m',how='outer')
  dfm = dfm.set_index(timeGroupby)
  dfm.drop('StartTime',axis=1,inplace=True)
  dfm.fillna(value=0,inplace=True)

  #dgbase.count().plot(ax=axtwin,style='o')
  #dgbase.count().plot(ax=axtwin,color='lightgrey',linestyle='-.')
  dfm.plot(ax=axtwin,color='lightgrey',linestyle='--',legend=True,label='Count')
  axtwin.set_ylim(ymin=0)
  logging.warning("title " + title)
  f=str(title).translate(None,' /.,:;\[]()-') + '.png'
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
  logging.warning("graphing " + title)
  if datas.empty :
    return
  dg=datas.groupby(timeGroupby)['ResponseTime']
  graphBasicsNew(title + 'Mean, Max : ', dg, [ 
    { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
    { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
    ])
  #graphBasicsNew(title + 'Quantiles : ', dg, [ 
  #  { 'aggr' : 'Q99', 'dgaggr' : dg.quantile(0.99), 'color' : 'black'},
  #  { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'grey'},
  #  { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'lightgrey'},
  #  ])
  

#--------------------------------------------------------------------------------------
def myGraphsErrors(datas,title,color='red') :
  if datas.empty :
    return
  dg=datas.groupby(timeGroupby)['Error']
  #logging.warning(dg.sum())
  graphAggregated('Sum', dg.sum() ,title, color)


#--------------------------------------------------------------------------------------
def groupByDescribe(datas,grps) :
  logging.warning("groupByDescribe " + str(grps))
  if datas.empty :
    return
  dg=datas.groupby(grps)['ResponseTime']
  OUT.out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=percentiles))

#--------------------------------------------------------------------------------------
def autofocus(datas) :
  dg=datas.groupby('PurePath')
  logging.warning("Full dg")
  logging.warning(dg.describe())
  logging.warning("Filtered dg")
  dg1=dg.filter(lambda x: x['ResponseTime'].mean() > 1000)
  logging.warning("dg1 dg")
  logging.warning(dg1.describe())
  sys.exit()

#--------------------------------------------------------------------------------------
def runIt(OUT) :
  DFF=DFFormatter(sys.argv[1],sys.argv[2],OUT)
  rawDatas=DFF.getDf()
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
  dfFocus=dfOK[ dfOK['PurePath'].isin( ["/dmp/creation/recherchepatientparcartevitale","/si-dmp-server/v1/services//repository","/rechercherpatient"])]
  autofocus(dfOK)

  dfall=pd.DataFrame(dfOK.groupby(timeGroupby)['StartTime'].count().apply(lambda x: 0))
  myGraphs(dfOK,'All OK')

  OUT.h2("Analyzing selected transaction")
  #dfFocus=dfOK[ dfOK['PurePath'].isin( DFF.getInterestingPurepaths()) ]
  #groupByDescribe(dfOK,["PurePath"])
  #groupByDescribe(dfOK,["PurePath"])
  groupByDescribe(dfFocus,["PurePath"])

  #for pp in dfOK['PurePath'].unique() :
  for pp in DFF.getInterestingPurepaths() :
    myGraphs(dfOK[dfOK['PurePath'] == pp], pp)

  OUT.h2("Analyzing transactions with response time > " + str(HIGHRESPONSETIME) )
  groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > HIGHRESPONSETIME ) ],["PurePath"])
  OUT.out("Samples OK having high resp time ",dfOK[ ( dfOK['ResponseTime'] > HIGHRESPONSETIME ) ])

  OUT.h2("Detail of transactions in error state")
  OUT.out("Samples KO failed ",dfKO)
  #OUT.out("Rawdatas detail",dfOK)

#--------------------------------------------------------------------------------------
@click.command()
@click.option('--datafile', help='datafile')
@click.option('--formatter', prompt='formatter')
@click.option('--output', default='html', type=click.Choice(['html', 'tty']))
@click.option('--pandas', prompt='pandas')

def go(OUT) :
  p=Param()
  p.set('datafile',datafile)
  p.set('output',output)
  p.set('formatter',formatter)
  p.set('pandas',pandas)


#--------------------------------------------------------------------------------------
if __name__ == '__main__':
  logging.basicConfig(format="%(asctime)s f=%(funcName)s %(levelname)s %(message)s", level=logging.WARNING)
  OUT=OutputHtml()
  OUT=OutputTty()
  OUT.open()
  go()

