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
    logging.debug("graphBasics aggr=" + id)
    plt.figure(figsize=(16,4))
    fig, ax=plt.subplots(figsize=(16,4))
    fig.autofmt_xdate()
    logging.debug("graphBasics setting ax")
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('fig.autofmt_xdate fixes the labels')
    ax.xaxis.set_major_formatter(mdates.DateFormatter(self.p['timeFormat']))
    ax.set_ylabel('Time ms', color='black')
    title=id
    self.dfall.plot(rot=45,ax=ax,grid=True,linewidth=0)
    for dg in dgList : 
      style=self.param.getGraphStyle(dg['aggr'])
      dg['dgaggr'].plot(title=dg['aggr'],rot=45,ax=ax,grid=True,color=style['color'],legend=True,label=dg['aggr'],linewidth=style['linewidth'])
      if dg['dgaggr'].count() < 50 :
        dg['dgaggr'].plot(title=dg['aggr'],rot=45,ax=ax,grid=True,legend=True,label=dg['aggr'],style=style['point'])
      ax.set_ylim(ymin=0)
    logging.debug("graphBasics setting axtwin")
    axtwin=ax.twinx()
    axtwin.set_ylabel('Count', color='lightgrey')
    dfCount=dgbase.count().reset_index()
    dfm=pd.merge_ordered(self.dfall,dfCount,left_on=self.p['timeGroupby'],right_on=self.p['timeGroupby'],how='outer')
    dfm = dfm.set_index(self.p['timeGroupby'])
    dfm.drop('StartTime',axis=1,inplace=True)
    dfm.fillna(value=0,inplace=True)
  
    #dgbase.count().plot(ax=axtwin,style='o')
    #dgbase.count().plot(ax=axtwin,color='lightgrey',linestyle='-.')
    dfm.plot(ax=axtwin,color='lightgrey',linestyle='--',legend=True,label='Count')
    axtwin.set_ylim(ymin=0)
    logging.debug("title " + title)
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
    plt.close()
    self.p['out'].image(f,title)
  
  #--------------------------------------------------------------------------------------
  def myGraphs(self,datas,title,describe=['Agent','PurePath']) :
    logging.debug("graphing " + title)
    if datas.empty :
      return
    self.p['out'].h3("Statistics and graph : " + title)
    dg=datas.groupby(self.p['timeGroupby'])['ResponseTime']
    for d in describe :
      self.groupByDescribe(datas,[d])
    #self.groupByDescribe(datas,["Agent"])
    #self.groupByDescribe(datas,["PurePath"])
    self.graphBasicsNew(title, dg, [ 
      { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
      { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
      { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'green'},
      { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'green'},
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
    logging.debug("groupByDescribe " + str(grps))
    if datas.empty :
      return
    dg=datas.groupby(grps)['ResponseTime']
    self.p['out'].out("GroupBy " + str(grps) + " statistics" ,dg.describe(percentiles=self.percentiles))
  
  #--------------------------------------------------------------------------------------
  def autofocus(self,datas) :
    dg=datas.groupby('PurePath',as_index=False).agg({"ResponseTime": ['mean', 'count']})
    #dg.columns=dg.columns.droplevel(level=0)
    dg.columns=["_".join(x) for x in dg.columns.ravel()]
    dg1=dg[ ( dg['ResponseTime_mean'] >= self.p['autofocusmean'] ) & ( dg['ResponseTime_count'] >= self.p['autofocuscount'] ) ]
    return(dg1["PurePath_"].values.tolist())
  
  #--------------------------------------------------------------------------------------
  def go(self) :
    #DFF=DFFormatter(self.p['datafile'],self.p['formatfile'],self.p['out'])
    DFF=DFFormatter(self.p)
    rawDatas=DFF.getDf()
    logging.debug(rawDatas)
    
    dfOK=rawDatas[ ( rawDatas['ErrorState'] == 'OK' ) ]
    dfKO=rawDatas[ ( rawDatas['ErrorState'] != 'OK') ]
    self.dfall=pd.DataFrame(dfOK.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
    DFF.setAutofocus(self.autofocus(dfOK))
    dfFocus=dfOK[ dfOK['PurePath'].isin( DFF.getFocusedPurepaths()) ]
  
    self.p['out'].h2("Analyzing transactions in status OK ")
    self.p['out'].out("File statistics",dfOK['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
    self.myGraphs(dfOK, 'AllOk',["Agent"])

    self.p['out'].h2("Analyzing transactions in Error ")
    self.myGraphs(dfKO,'All Errors')
  
    self.p['out'].h2("Analyzing focused transactions")

    self.p['out'].h3("Focus details")
    self.p['out'].p("--autofocusmean : " + str(self.p['autofocusmean']))
    self.p['out'].p("--autofocuscount : " + str(self.p['autofocuscount']))

    self.p['out'].out("File statistics",dfFocus['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
    self.myGraphs(dfFocus,'Focus')
  
    #for pp in dfOK['PurePath'].unique() :
    for pp in DFF.getFocusedPurepaths() :
      self.myGraphs(dfOK[dfOK['PurePath'] == pp], pp)
  
    self.p['out'].h2("Analyzing transactions with response time > " + str(self.p['highResponseTime']) )
    self.p['out'].h3("Statistics")
    self.groupByDescribe(dfOK[ ( dfOK['ResponseTime'] > self.p['highResponseTime'] ) ],["PurePath"])
    self.myGraphs(dfOK[ ( dfOK['ResponseTime'] > self.p['highResponseTime'] ) ],'HighResponseTime')
    self.p['out'].out("Samples OK having high resp time ",dfOK[ ( dfOK['ResponseTime'] > self.p['highResponseTime'] ) ])
  
    self.p['out'].h2("Detail of transactions in error state")
    self.p['out'].out("Samples KO failed ",dfKO)

    self.p['out'].h2("More details on transactions OK")
    self.myGraphs(dfOK, 'AllOk')

    #self.p['out'].out("Rawdatas detail",dfOK)
  
