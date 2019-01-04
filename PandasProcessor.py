import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
from Outer import *
from DFFormatter import *
from PandasGrapher import *
from Param import *
  
STEPS=dict()
#----------------------------------------------------------------
def Step(name) :
  def Stepped(f) :
    STEPS[name]=f
    def wrapper(*args,**kwargs) :
      a=list(args)
      return(f(*args))
    return(wrapper)
  return(Stepped)

#----------------------------------------------------------------
class PandasProcessor() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.param=param
    self.setBehavior()
    self.DFF=DFFormatter(self.p)

  #--------------------------------------------------------------------------------------
  def setBehavior(self) :
    self.p=self.param.getAll()
    self.quick=self.p['quick']
    self.nodescribe=self.p['nodescribe']
    self.nographs=self.p['nographs']
    self.nobuckets=self.p['nobuckets']
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    self.timeregex=self.p['timeregex']
    self.percentiles=[.50,.95,.99]
    self.buckets=self.p['buckets']
    self.fileCounter=0
    self.steps=self.p['steps']
    self.grapher=PandasGrapher(self.param)
    pd.options.display.float_format = '{:.0f}'.format

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
  def myBuckets(self,datas,title):
    logging.warning("buckets begin " + title)
    self.p['out'].h4("Buckets for " + title)
    bins=pd.cut(datas['ResponseTime'],self.buckets)
    logging.warning("datas binning " + title)
    dg=datas.groupby(bins)['ResponseTime']
    logging.warning("datas binned " + title)
    self.p['out'].out(title + " buckets",dg.describe(percentiles=self.percentiles))
    if not self.nobuckets :
      self.grapher.myPlotBar(dg,'Buckets for ' + title)
    #else :
    #  self.p['out'].out(title + " buckets",dg.describe(percentiles=self.percentiles))
    logging.warning("buckets end " + title)

  #--------------------------------------------------------------------------------------
  def describe(self,datas,title,describe):
    logging.warning("describe begin " + title)
    self.p['out'].h4("Grouping for " + title)
    if self.nodescribe :
      self.groupByDescribe(datas,'PurePath',title)
    else :
      for d in describe :
        self.groupByDescribe(datas,[d],title)
    logging.warning("describe end " + title)

  #--------------------------------------------------------------------------------------
  def myGraphs(self,datas,title,describe=['Agent','PurePath','Application']) :
    logging.warning("myGraphs begin " + title)
    if datas.empty :
      return
    self.p['out'].h3("Statistics and graph : " + title)

    self.myBuckets(datas,title) 
    self.describe(datas,title,describe)

    dg=datas.groupby(self.p['timeGroupby'])['ResponseTime']
    if self.nographs :
      #self.p['out'].out(title, datas.groupby('PurePath').describe(percentiles=self.percentiles))
      pass
    else :
      self.p['out'].h4("Time view for " + title)
      self.grapher.graphBasicsNew("Time view " + title, dg, [ 
      { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
      { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
      { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'green'},
      { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'green'},
      ])
    logging.warning("myGraphs end " + title)
  
  #--------------------------------------------------------------------------------------
  def groupByDescribe(self,datas,grps,title='') :
    logging.warning("groupByDescribe " + str(grps))
    if datas.empty :
      return
    dg=datas.groupby(grps)['ResponseTime']
    self.p['out'].out("GroupBy "  +  str(grps) + " " + title + " statistics" ,dg.describe(percentiles=self.percentiles))
    if not self.nographs :
      self.grapher.myPlotBar(datas.groupby(grps)['ResponseTime'],str(grps) + " " + title)
  
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
  @Step('Formatfile')
  def printProcessing(self) :
    self.p['out'].h2("Formatfile details ")
    self.p['out'].p(str(self.DFF.getInfos('json')))

  #--------------------------------------------------------------------------------------
  @Step('Params')
  def printParams(self) :
    self.p['out'].h2("Param informations")
    self.p['out'].p(self.param.getAllAsString())

  #--------------------------------------------------------------------------------------
  @Step('Stats')
  def printStats(self) :
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

  #--------------------------------------------------------------------------------------
  @Step('File')
  def printFile(self) :
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
  @Step('OK')
  def printOK(self) :
    self.p['out'].h2("Analyzing " + str(len(self.dfOK)) + " transactions in status OK (" + str(self.filtered) + " have been filtered) ")
    self.myGraphs(self.dfOK, 'OK',["Agent","Application"])

  #--------------------------------------------------------------------------------------
  @Step('KO')
  def printKO(self) :
    self.p['out'].h2("Analyzing transactions in Error ")
    self.myGraphs(self.dfKO,'Errors')

  #--------------------------------------------------------------------------------------
  @Step('Focus')
  def printFocus(self) :
    self.p['out'].h2("Analyzing " + str(len(self.dfFocus)) + " focused transactions")
    self.myGraphs(self.dfFocus,'Focus')
    #for pp in self.dfOK['PurePath'].unique() :
    for pp in self.DFF.getFocusedPurepaths() :
      self.myGraphs(self.dfOK[self.dfOK['PurePath'] == pp], 'Focus ' + pp)

  #--------------------------------------------------------------------------------------
  @Step('HighResponseTime')
  def printHighResponseTime(self) :
    self.p['out'].h2("Analyzing transactions with response time > " + str(self.p['highResponseTime']) )
    #self.p['out'].h3("Statistics")
    #self.groupByDescribe(self.dfOK[ ( self.dfOK['ResponseTime'] > self.p['highResponseTime'] ) ],["PurePath"],'HighResponseTime')
    self.myGraphs(self.dfHigh,'HighResponseTime')
    if not self.quick :
      for pp in self.dfHigh['PurePath'].unique() :
        if self.dfHigh[self.dfHigh['PurePath'] == pp]['ResponseTime'].count() > 10 :
          self.myGraphs(self.dfHigh[self.dfHigh['PurePath'] == pp], 'HighResponseTime Detail' + pp)
      self.p['out'].out("Samples OK having high resp time ",self.dfHigh)

  #--------------------------------------------------------------------------------------
  @Step('KODetails')
  def printKODetails(self) :
    if not self.quick :
      self.p['out'].h2("Detail of transactions in error state")
      self.p['out'].out("Samples KO failed ",self.dfKO)

  #--------------------------------------------------------------------------------------
  def buildDataframes(self) :
    rawdatas=self.DFF.getDf()
    rawdatas=self.filter(rawdatas)
    self.dfOK=rawdatas[ ( rawdatas['ErrorState'] == 'OK' ) ]
    self.dfKO=rawdatas[ ( rawdatas['ErrorState'] != 'OK') ]
    self.dfall=pd.DataFrame(self.dfOK.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
    self.grapher.setDfall(self.dfall)
    self.DFF.setAutofocus(self.autofocus(self.dfOK))
    self.dfFocus=self.dfOK[ self.dfOK['PurePath'].isin( self.DFF.getFocusedPurepaths()) ]
    self.dfHigh=self.dfOK[ ( self.dfOK['ResponseTime'] > self.p['highResponseTime'] ) ]

  #--------------------------------------------------------------------------------------
  def go(self) :
    logging.warning("Start")
    self.buildDataframes()
    self.printTitle()
    for s in self.steps :
      STEPS[s](self)
    logging.warning("End")
  
