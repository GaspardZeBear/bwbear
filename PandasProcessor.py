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

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.param=param
    self.param.processParam()
    self.p=self.param.getAll()
    self.quick=self.p['quick']
    self.nodescribe=self.p['nodescribe']
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    self.timeregex=self.p['timeregex']
    self.percentiles=[.50,.95,.99]
    self.buckets=self.p['buckets']
    self.fileCounter=0
    pd.options.display.float_format = '{:.0f}'.format
    self.DFF=DFFormatter(self.p)
    self.go()

  #--------------------------------------------------------------------------------------
  def getPngFileName(self,s) :
    self.fileCounter += 1
    n=str(s).translate(None,' /.,:;\[]()-*') + str(self.fileCounter) + '.png'
    #n=str(s).translate(None,' \'/.,:;\[]()-*') + '.png'
    logging.warning(n)
    return(n)
  
  #--------------------------------------------------------------------------------------
  def graphBasicsNew(self,title,dgbase,dgList) :
    logging.debug("graphBasics aggr=" + title)
    plt.figure(figsize=(16,4))
    fig, ax=plt.subplots(figsize=(16,4))
    fig.autofmt_xdate()
    logging.debug("graphBasics setting ax")
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('fig.autofmt_xdate fixes the labels')
    ax.xaxis.set_major_formatter(mdates.DateFormatter(self.p['timeFormat']))
    ax.set_ylabel('Time ms', color='black')
    self.dfall.plot(rot=45,ax=ax,grid=True,linewidth=0)
    for dg in dgList : 
      style=self.param.getGraphStyle(dg['aggr'])
      dg['dgaggr'].plot(title=title,rot=45,ax=ax,grid=True,color=style['color'],legend=True,label=dg['aggr'],linewidth=style['linewidth'])
      if dg['dgaggr'].count() < 50 :
        dg['dgaggr'].plot(title=title,rot=45,ax=ax,grid=True,legend=True,label=dg['aggr'],style=style['point'])
      if self.p['ymax'] > 0 :
        ax.set_ylim(ymin=0,ymax=self.p['ymax'])
      else :
        ax.set_ylim(ymin=0)
    logging.debug("graphBasics setting axtwin")
    axtwin=ax.twinx()
    axtwin.set_ylabel('Count', color='lightgrey')
    dfCount=dgbase.count().reset_index()
    dfm=pd.merge_ordered(self.dfall,dfCount,left_on=self.p['timeGroupby'],right_on=self.p['timeGroupby'],how='outer')
    dfm = dfm.set_index(self.p['timeGroupby'])
    dfm.drop('StartTime',axis=1,inplace=True)
    dfm.fillna(value=0,inplace=True)
  
    dfm.plot(ax=axtwin,color='lightgrey',linestyle='--',legend=False,label='Count')
    axtwin.set_ylim(ymin=0)
    logging.debug("title " + title)
    f=self.getPngFileName(str(title))
    plt.savefig(f)
    plt.close()
    self.p['out'].image(f,title)
  
  
  #--------------------------------------------------------------------------------------
  def myPlotBar(self,datas,title) :
    dc=datas.count() 
    dm=datas.mean() 
    if dc.empty :
      return
    if dc.size > 100 :
      return
    logging.warning(datas)
    df=dc.to_frame()
    df.rename(columns={"ResponseTime":"Count"},inplace=True)
    dfm=dm.to_frame()
    dfm.rename(columns={"ResponseTime":"Mean"},inplace=True)

    figYSize=int(dc.size/4) + 1

    fig=plt.figure(figsize=(16,figYSize))
    ax=fig.add_subplot(121)
    df.plot.barh(color='lightgrey',ax=ax,grid=True)
    ax.minorticks_on()
    ax.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
    axm=fig.add_subplot(122)
    dfm.plot.barh(color='green',ax=axm,grid=True)
    axm.minorticks_on()
    axm.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
    axm.get_yaxis().set_ticks([])

    f=self.getPngFileName(title)
    plt.tight_layout()
    plt.savefig(f)
    plt.close()
    self.p['out'].image(f,title)

  #--------------------------------------------------------------------------------------
  def timeregexFilter(self,val):
    if val:
        mo = re.search(self.timeregex,val)
        if mo:
            return True
        else:
            return False
    else:
        return False


  #--------------------------------------------------------------------------------------
  def regexFilter(self,val):
    if val:
        mo = re.search(self.ppregex,val)
        if mo:
            return True
        else:
            return False
    else:
        return False

  #--------------------------------------------------------------------------------------
  def regexcludeFilter(self,val):
    if val:
        mo = re.search(self.ppregexclude,val)
        if mo:
            return False
        else:
            return True
    else:
        return False


  #--------------------------------------------------------------------------------------
  def myGraphs(self,datas,title,describe=['Agent','PurePath','Application']) :
    logging.warning("myGraphs " + title)
    if datas.empty :
      return
    self.p['out'].h3("Statistics and graph : " + title)
    bins=pd.cut(datas['ResponseTime'],self.buckets)
    #bins=pd.cut(datas['ResponseTime'],3)
    dg=datas.groupby(bins)['ResponseTime']
    self.myPlotBar(dg,'Buckets for ' + title)
    dg=datas.groupby(self.p['timeGroupby'])['ResponseTime']
    if self.nodescribe :
      self.groupByDescribe(datas,'PurePath',title)
    else :
      for d in describe :
        self.groupByDescribe(datas,[d],title)
    self.graphBasicsNew("Time vision " + title, dg, [ 
      { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
      { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
      { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'green'},
      { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'green'},
      ])
  
  #--------------------------------------------------------------------------------------
  def groupByDescribe(self,datas,grps,title='') :
    logging.warning("groupByDescribe " + str(grps))
    #if self.nodescribe :
    #  return
    if datas.empty :
      return
    dg=datas.groupby(grps)['ResponseTime']
    self.p['out'].out("GroupBy "  +  str(grps) + " " + title + " statistics" ,dg.describe(percentiles=self.percentiles))
    self.myPlotBar(datas.groupby(grps)['ResponseTime'],str(grps) + " " + title)
  
  #--------------------------------------------------------------------------------------
  def autofocus(self,datas) :
    dg=datas.groupby('PurePath',as_index=False).agg({"ResponseTime": ['mean', 'count']})
    #dg.columns=dg.columns.droplevel(level=0)
    dg.columns=["_".join(x) for x in dg.columns.ravel()]
    dg1=dg[ ( dg['ResponseTime_mean'] >= self.p['autofocusmean'] ) & ( dg['ResponseTime_count'] >= self.p['autofocuscount'] ) ]
    return(dg1["PurePath_"].values.tolist())
  
  #--------------------------------------------------------------------------------------
  def filter(self,rawdatas) :
    sizein=len(rawdatas)
    if len(self.ppregex) > 0 :
      rawdatas=rawdatas[rawdatas['PurePath'].apply(self.regexFilter)]
    if len(self.ppregexclude) > 0 :
      rawdatas=rawdatas[rawdatas['PurePath'].apply(self.regexcludeFilter)]
    if len(self.timeregex) > 0 :
      logging.warning("Apply timeregex filter")
      rawdatas=rawdatas[rawdatas['StartTimeStr'].apply(self.timeregexFilter)]
    self.filtered=sizein - len(rawdatas.index)
    return(rawdatas)

  #--------------------------------------------------------------------------------------
  def printTitle(self) :
    self.p['out'].h1("Analyzing file " + self.DFF.getInfos('Datafile'))

  #--------------------------------------------------------------------------------------
  def printProcessing(self) :
    self.p['out'].h1("Analyzing file " + self.DFF.getInfos('Datafile'))
    self.p['out'].h2("Formatfile details ")
    self.p['out'].p(str(self.DFF.getInfos('json')))
    self.p['out'].h2("Param informations")
    self.p['out'].p(self.param.getAllAsString())
    self.p['out'].h2("Stats informations")
    ths={
       "1.Init"  : self.DFF.getDf()['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame(),
       "2.OK"    : self.dfOK['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame(),
       "3.KO"    : self.dfKO['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame(),
       "4.Focus" : self.dfFocus['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame(),
       "5.HighRespTime" : self.dfHigh['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame()
    }
    self.p['out'].tables(ths)
    if self.quick :
      return
    self.p['out'].h2("File informations")
    self.p['out'].out("Initial head",self.DFF.getInfos('HeadInitial'))
    if self.DFF.isWrangled() :
      self.p['out'].out("Final head",self.DFF.getInfos('HeadFinal'))
    self.p['out'].out("Initial tail",self.DFF.getInfos('TailInitial'))
    if self.DFF.isWrangled() :
      self.p['out'].out("Final tail",self.DFF.getInfos('TailFinal'))
    #self.p['out'].out("Initial file",self.DFF.getInfos('DescribeInitial'))
    if self.DFF.isWrangled() :
      self.p['out'].out("Final file",self.DFF.getInfos('DescribeFinal'))

  #--------------------------------------------------------------------------------------
  def printOK(self) :
    self.p['out'].h2("Analyzing " + str(len(self.dfOK)) + " transactions in status OK (" + str(self.filtered) + " have been filtered) ")
    self.myGraphs(self.dfOK, 'OK',["Agent","Application"])

  #--------------------------------------------------------------------------------------
  def printKO(self) :
    self.p['out'].h2("Analyzing transactions in Error ")
    self.myGraphs(self.dfKO,'Errors')

  #--------------------------------------------------------------------------------------
  def printFocus(self) :
    self.p['out'].h2("Analyzing " + str(len(self.dfFocus)) + " focused transactions")
    self.myGraphs(self.dfFocus,'Focus')
    #for pp in self.dfOK['PurePath'].unique() :
    for pp in self.DFF.getFocusedPurepaths() :
      self.myGraphs(self.dfOK[self.dfOK['PurePath'] == pp], 'Focus ' + pp)

  #--------------------------------------------------------------------------------------
  def printHighResponseTime(self) :
    self.p['out'].h2("Analyzing transactions with response time > " + str(self.p['highResponseTime']) )
    #self.p['out'].h3("Statistics")
    #self.groupByDescribe(self.dfOK[ ( self.dfOK['ResponseTime'] > self.p['highResponseTime'] ) ],["PurePath"],'HighResponseTime')
    self.myGraphs(self.dfHigh,'HighResponseTime')
    if not self.quick :
      for pp in self.dfHigh['PurePath'].unique() :
        if self.dfHigh[self.dfHigh['PurePath'] == pp]['ResponseTime'].count() > 10 :
          self.myGraphs(self.dfHigh[self.dfHigh['PurePath'] == pp], 'HighResponseTime ' + pp)
      self.p['out'].out("Samples OK having high resp time ",self.dfHigh)

  #--------------------------------------------------------------------------------------
  def printKODetails(self) :
    if not self.quick :
      self.p['out'].h2("Detail of transactions in error state")
      self.p['out'].out("Samples KO failed ",self.dfKO)

  #--------------------------------------------------------------------------------------
  def printOKDetails(self) :
    if not self.quick :
      self.p['out'].h2("More details on transactions OK")
      self.myGraphs(self.dfOK, 'OK')

  #--------------------------------------------------------------------------------------
  def buildDataframes(self) :
    rawdatas=self.DFF.getDf()
    rawdatas=self.filter(rawdatas)
    self.dfOK=rawdatas[ ( rawdatas['ErrorState'] == 'OK' ) ]
    self.dfKO=rawdatas[ ( rawdatas['ErrorState'] != 'OK') ]
    self.dfall=pd.DataFrame(self.dfOK.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
    self.DFF.setAutofocus(self.autofocus(self.dfOK))
    self.dfFocus=self.dfOK[ self.dfOK['PurePath'].isin( self.DFF.getFocusedPurepaths()) ]
    self.dfHigh=self.dfOK[ ( self.dfOK['ResponseTime'] > self.p['highResponseTime'] ) ]

  #--------------------------------------------------------------------------------------
  def go(self) :
    logging.warning("Start")
    self.buildDataframes()
    self.printTitle()
    self.printProcessing()
    self.printOK()
    self.printKO()
    self.printFocus()
    self.printHighResponseTime()
    self.printKODetails()
    self.printOKDetails()
    logging.warning("End")
  
