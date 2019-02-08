import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
import json
import re
import hashlib
from Outer import *
from PandasGrapher import *
from PPDFFilterer import *
from PPStator import *
from DFFormatter import *
 
#--------------------------------------------------------------------------------------
class PPFramor() :

  pd.options.display.float_format = '{:.0f}'.format
  database=''
  fileNum=0
  databaseNum=0
  sqlNum=0

  #--------------------------------------------------------------------------------------
  def __init__(self,param,file,tsm=None) :
    self.param=param
    self.tsm=tsm
    self.p=self.param.getAll()
    logging.warning("PPFramor begins")
    self.file=file
    self.decimal='.'
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    self.percentiles=self.p['percentiles']
    PPFramor.fileNum += 1
    self.setRawdatas()
    self.report()
    logging.warning("PPFramor ends")

#--------------------------------------------------------------------------------------
  def getRawdatas(self) :
    return(self.rawdatas)

#--------------------------------------------------------------------------------------
  def getDatas(self) :
    return(self.datas)
#--------------------------------------------------------------------------------------
  def getFile(self) :
    return(self.file)

#--------------------------------------------------------------------------------------
  def setRawdatas(self) :
    self.p['datafile']=self.file
    self.DFF=DFFormatter.getFromFactory(self.p['type'],self.p)
    
    ppf=PPDFFilterer(self.DFF.getDf(),self.param)
    self.datas=ppf.getDfOK()
    self.tsmList=self.datas['ts10m'].unique()
    if self.tsm is not None:
      self.datas=self.datas[ self.datas['ts10m'] == self.tsm ]
    self.rawdatas=self.datas.groupby('PurePath')['ResponseTime'].describe(percentiles=self.percentiles)

#--------------------------------------------------------------------------------------
  def report(self) :
    self.p['out'].h2("PP from " + self.file)
    self.ppStator=PPStator(self.param,self.datas)
    with pd.option_context('display.max_rows', None, 'display.max_colwidth', 0, 'display.float_format','{:.2f}'.format) :
      self.p['out'].out("Summary stats",self.ppStator.getXstats(),escape=False)

#--------------------------------------------------------------------------------------
  def getTsmlist(self,tsm) :
    return(self.tsmList)

#--------------------------------------------------------------------------------------
class PPComparator() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param,f1,f2) :
    self.param=param
    self.p=self.param.getAll()
    self.grapher=PandasGrapher(self.param)
    self.f1=f1
    self.f2=f2
    self.df1=f1.getRawdatas()
    self.df2=f2.getRawdatas()
    self.go()

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaCountPe(x) :
    return(PPComparator.deltaPe('count',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaStdPe(x) :
    return(PPComparator.deltaPe('std',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaMeanPe(x) :
    return(PPComparator.deltaPe('mean',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaP50Pe(x) :
    return(PPComparator.deltaPe('50%',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaP95Pe(x) :
    return(PPComparator.deltaPe('95%',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaPe(field,x) :
    kx=field+"_x"
    ky=field+"_y"
    if x[kx] > 0 :
      return(100*(x[ky]-x[kx])/x[kx])
    return(0)

  #--------------------------------------------------------------------------------------
  def go(self) :
    #print(self.df1)
    #print(self.df2)
    dfm=pd.merge(self.df1,self.df2,on='PurePath',how='outer')
    dfm.reset_index(inplace=True)
    dfm['DMax']=dfm.apply(lambda x: x['max_y'] - x['max_x'],axis=1 ) 
    dfm['DStd']=dfm.apply(lambda x: x['std_y'] - x['std_x'],axis=1 ) 
    dfm['DCount']=dfm.apply(lambda x: x['count_y'] - x['count_x'],axis=1 ) 
    dfm['DMean']=dfm.apply(lambda x: x['mean_y'] - x['mean_x'],axis=1 ) 
    dfm['DP50']=dfm.apply(lambda x: x['50%_y'] - x['50%_x'],axis=1 ) 
    dfm['DP95']=dfm.apply(lambda x: x['95%_y'] - x['95%_x'],axis=1 ) 
    dfm['DStd%']=dfm.apply(PPComparator.deltaStdPe,axis=1 ) 
    dfm['DCount%']=dfm.apply(PPComparator.deltaCountPe,axis=1 ) 
    dfm['DMean%']=dfm.apply(PPComparator.deltaMeanPe,axis=1 ) 
    dfm['DP50%']=dfm.apply(PPComparator.deltaP50Pe,axis=1 ) 
    dfm['DP95%']=dfm.apply(PPComparator.deltaP95Pe,axis=1 ) 
    dfm.fillna(value=0,inplace=True)
    filter=True
    if filter :
      #dfm=dfm[(dfm['count_x'] > self.p['autofocuscount']) | (dfm['count_y'] > self.p['autofocuscount']) ]
      #dfm=dfm[(dfm['mean_x'] > self.p['autofocusmean']) | (dfm['mean_y'] > self.p['autofocusmean']) ]
      #dfm=dfm[(abs(dfm['DMeanPe']) > 10)]
      pass
    #logging.warning(dfm)
    if dfm.size == 0 :
      return
    with pd.option_context('display.max_rows', None) :
      self.p['out'].h2("Comparison of requests : x=" + self.f1.getFile() + " y=" + self.f2.getFile())
      self.p['out'].out("Compare",dfm[['PurePath','count_x','count_y','DCount','DCount%',
          'mean_x','mean_y','DMean','DMean%',
          'std_x','std_y','DStd','DStd%',
          '50%_x','50%_y','DP50','DP50%',
          '95%_x','95%_y','DP95','DP95%',
          'max_x','max_y','DMax']],
          escape=False,classes='tablePPcompareProcessor')
      self.graphIt(self.f1.getFile(),self.f1.getDatas())
      self.graphIt(self.f2.getFile(),self.f2.getDatas())

  #--------------------------------------------------------------------------------------
  def graphIt(self,title,df) :
      self.dfall=pd.DataFrame(df.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
      self.grapher.setDfall(self.dfall)
      dg=df.groupby(self.p['timeGroupby'])['ResponseTime']
      self.p['out'].h3("Time view for " + title)
      self.grapher.graphBasicsNew("Time view " + title, dg, [
      { 'aggr' : 'Max', 'dgaggr' : dg.max(), 'color' : 'red'},
      { 'aggr' : 'Mean', 'dgaggr' : dg.mean(), 'color' : 'green'},
      { 'aggr' : 'Q50', 'dgaggr' : dg.quantile(0.5), 'color' : 'green'},
      { 'aggr' : 'Q95', 'dgaggr' : dg.quantile(0.95), 'color' : 'green'},
      ])



#--------------------------------------------------------------------------------------
class PPCompareProcessor() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.param=param
    self.p=self.param.getAll()
    self.p['out'].setPPdiv("PPCompareProcessor")
    self.dfs=[]
    logging.warning(self.p)
    if ('file2' in self.p) & (self.p['file2'] is not None) :
      self.p['out'].h1('PPCompareProcessor compare ' + self.p['file1'] + ' and ' + self.p['file2'])
      self.dfs.append(PPFramor(self.param,self.p['file1']))
      self.dfs.append(PPFramor(self.param,self.p['file2']))
    else :
      self.p['out'].h1('PPCompareProcessor autocompare ' + self.p['file1'])
      fr=PPFramor(self.param,self.p['file1'])
      for tsm in fr.getTsmlist('ts10m') :
        self.dfs.append(PPFramor(self.param,self.p['file1'],tsm))
      pass

  #--------------------------------------------------------------------------------------
  def setBehavior(self) :
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    pd.options.display.float_format = '{:.0f}'.format

  #--------------------------------------------------------------------------------------
  def go(self) :
    for i in range(0,len(self.dfs)-1) :
      PPComparator(self.param,self.dfs[i],self.dfs[i+1])

