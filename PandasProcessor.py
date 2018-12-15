import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
from Outer import *
from DFFormatter import *
from Param import *
  
class PandasProcessor() :

  def __init__(self,param) :
    self.param=param
    self.param.processParam()
    self.p=self.param.getAll()
    self.percentiles=[.50,.95,.99]
    pd.options.display.float_format = '{:.0f}'.format
    self.go()

  #--------------------------------------------------------------------------------------
  def graphAggregated(self,aggr,dgAggr,title,color='blue') :
    plt.figure(figsize=(16,4))
    fig, ax=plt.subplots(figsize=(16,4))
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('fig.autofmt_xdate fixes the labels')
    ax.xaxis.set_major_formatter(mdates.DateFormatter(self.p['timeFormat']))
    dgAggr.plot(title=aggr + " " + title,color=color,rot=45,ax=ax,grid=True)
    f=title + aggr + '.png'
    plt.savefig(f)
    plt.close()
    self.p['out'].image(f,aggr + " " +title)

  
  #--------------------------------------------------------------------------------------
  def graphBasicsNew(self,id,dgbase,dgList) :
    logging.warning("graphBasics aggr=" + id)
    plt.figure(figsize=(16,4))
    fig, ax=plt.subplots(figsize=(16,4))
    fig.autofmt_xdate()
    logging.warning("graphBasics setting ax")
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('fig.autofmt_xdate fixes the labels')
    ax.xaxis.set_major_formatter(mdates.DateFormatter(self.p['timeFormat']))
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
    dfm = dfm.set_index(self.p['timeGroupby'])
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
    self.p['out'].image(f,title)
  
  
  #--------------------------------------------------------------------------------------
  def myPlotBarResponseTime(self,datas,title,color='blue') :
    if datas.empty :
      return
    rtime=datas['ResponseTime']
    plt.figure(figsize=(17,4))
    rtime.plot.bar(title=title,rot=45,color=color)
    f=title + '.png'
    plt.savefig(f)
    self.p['out'].image(f,title)
  
  #--------------------------------------------------------------------------------------
  def myGraphs(self,datas,title,color='blue') :
    logging.warning("graphing " + title)
    if datas.empty :
      return
    dg=datas.groupby(self.p['timeGroupby'])['ResponseTime']
    self.graphBasicsNew(title + 'Mean, Max : ', dg, [ 
      { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
      { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
      ])
    #self.graphBasicsNew(title + 'Quantiles : ', dg, [ 
    #  { 'aggr' : 'Q99', 'dgaggr' : dg.quantile(0.99), 'color' : 'black'},
    #  { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'grey'},
    #  { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'lightgrey'},
    #  ])
    
  
  #--------------------------------------------------------------------------------------
  def myGraphsErrors(self,datas,title,color='red') :
    if datas.empty :
      return
    dg=datas.groupby(self.p['timeGroupby'])['Error']
    #logging.warning(dg.sum())
    self.graphAggregated('Sum', dg.sum() ,title, color)
  
  
  #--------------------------------------------------------------------------------------
  def groupByDescribe(self,datas,grps) :
    logging.warning("groupByDescribe " + str(grps))
    if datas.empty :
      return
    dg=datas.groupby(grps)['ResponseTime']
    self.p['out'].out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=self.percentiles))
  
  #--------------------------------------------------------------------------------------
  def autofocus(self,datas) :
    dg=datas.groupby('PurePath')
    logging.warning("Full dg")
    logging.warning(dg.describe())
    logging.warning("Filtered dg")
    dg1=dg.filter(lambda x: x['ResponseTime'].mean() > 1000)
    logging.warning("dg1 dg")
    logging.warning(dg1.describe())
    sys.exit()
  
  #--------------------------------------------------------------------------------------
  def go(self) :
    DFF=DFFormatter(self.p['datafile'],self.p['formatfile'],self.p['out'])
    rawDatas=DFF.getDf()
    logging.debug(rawDatas)
    rawDatas=rawDatas[rawDatas.PurePath.str.contains("assets")==False]
  
    self.p['out'].h2("Analyzing transaction in Error ")
    self.myGraphsErrors(rawDatas,'All Errors over time')
    self.groupByDescribe(rawDatas,["ErrorState"])
    dfKO=rawDatas[ ( rawDatas['ErrorState'] != 'OK') ]
    self.groupByDescribe(dfKO,["Agent"])
    self.groupByDescribe(dfKO,["PurePath"])
    #self.myGraphs(dfKO,'All Errors')
  
    self.p['out'].h2("Analyzing transactions in status OK ")
    dfOK=rawDatas[ ( rawDatas['ErrorState'] == 'OK' ) ]
    self.groupByDescribe(dfOK,["Agent"])
    self.groupByDescribe(dfOK,["PurePath"])
    dfFocus=dfOK[ dfOK['PurePath'].isin( ["/dmp/creation/recherchepatientparcartevitale","/si-dmp-server/v1/services//repository","/rechercherpatient"])]
    self.autofocus(dfOK)
  
    dfall=pd.DataFrame(dfOK.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
    self.myGraphs(dfOK,'All OK')
  
    self.p['out'].h2("Analyzing selected transaction")
    #dfFocus=dfOK[ dfOK['PurePath'].isin( DFF.getInterestingPurepaths()) ]
    #self.groupByDescribe(dfOK,["PurePath"])
    #self.groupByDescribe(dfOK,["PurePath"])
    self.groupByDescribe(dfFocus,["PurePath"])
  
    #for pp in dfOK['PurePath'].unique() :
    for pp in DFF.getInterestingPurepaths() :
      self.myGraphs(dfOK[dfOK['PurePath'] == pp], pp)
  
    self.p['out'].h2("Analyzing transactions with response time > " + str(HIGHRESPONSETIME) )
    self.groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > HIGHRESPONSETIME ) ],["PurePath"])
    self.p['out'].out("Samples OK having high resp time ",dfOK[ ( dfOK['ResponseTime'] > HIGHRESPONSETIME ) ])
  
    self.p['out'].h2("Detail of transactions in error state")
    self.p['out'].out("Samples KO failed ",dfKO)
    #self.p['out'].out("Rawdatas detail",dfOK)
  