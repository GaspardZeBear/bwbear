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
 
#--------------------------------------------------------------------------------------
class PPFramor() :

  percentiles=[.50,.95,.99]
  pd.options.display.float_format = '{:.0f}'.format
  database=''
  fileNum=0
  databaseNum=0
  sqlNum=0

  #--------------------------------------------------------------------------------------
  def __init__(self,param,file) :
    self.param=param
    self.p=self.param.getAll()
    logging.warning("PPFramor begins")
    self.file=file
    self.decimal='.'
    PPFramor.fileNum += 1
    PPFramor.databaseNum  = 0 
    PPFramor.sqlNum  = 0 
    self.setRawdatas()
    logging.warning("PPFramor ends")

  @staticmethod
  def setPPId(row) :
    if row['Level'] == 1 :
      PPFramor.databaseNum += 1
      PPFramor.sqlNum = 1
    else :
      PPFramor.sqlNum += 1
    return(str(PPFramor.fileNum) + "." + str(PPFramor.databaseNum) + "." + str(PPFramor.sqlNum) ) 

  @staticmethod
  def setDatabase(row) :
    if row['Level'] == 1 :
      PPFramor.database = row['Sql']
    return(PPFramor.database)


#--------------------------------------------------------------------------------------
  def getRawdatas(self) :
    return(self.rawdatas)

#--------------------------------------------------------------------------------------
  def setRawdatas(self) :
    self.datas=pd.read_csv(self.file,sep=';',decimal=self.decimal)
    self.rawdatas=self.datas.groupby('PurePath')['ResponseTime'].describe(percentiles=PPFramor.percentiles)
    self.p['out'].h2("PP from " + self.file)
    with pd.option_context('display.max_rows', None, 'display.max_colwidth', 0) :
      self.p['out'].out("PP",self.rawdatas,False)

#--------------------------------------------------------------------------------------
class PPComparator() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param,df1,df2) :
    self.param=param
    self.p=self.param.getAll()
    self.df1=df1
    self.df2=df2
    self.go()

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaCountPercent(x) :
    return(PPComparator.deltaPercent('count',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaMeanPercent(x) :
    return(PPComparator.deltaPercent('mean',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaP50Percent(x) :
    return(PPComparator.deltaPercent('50%',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaP95Percent(x) :
    return(PPComparator.deltaPercent('95%',x))

  @staticmethod
  #--------------------------------------------------------------------------------------
  def deltaPercent(field,x) :
    kx=field+"_x"
    ky=field+"_y"
    if x[kx] > 0 :
      return(100*(x[ky]-x[kx])/x[kx])
    return(0)

  #--------------------------------------------------------------------------------------
  def go(self) :
    print(self.df1)
    print(self.df2)
    dfm=pd.merge(self.df1,self.df2,on='PurePath',how='outer')
    dfm['DeltaCount']=dfm.apply(lambda x: x['count_y'] - x['count_x'],axis=1 ) 
    dfm['DeltaMean']=dfm.apply(lambda x: x['mean_y'] - x['mean_x'],axis=1 ) 
    dfm['DeltaP50']=dfm.apply(lambda x: x['50%_y'] - x['50%_x'],axis=1 ) 
    dfm['DeltaP95']=dfm.apply(lambda x: x['95%_y'] - x['95%_x'],axis=1 ) 
    dfm['DeltaCountPercent']=dfm.apply(PPComparator.deltaCountPercent,axis=1 ) 
    dfm['DeltaMeanPercent']=dfm.apply(PPComparator.deltaMeanPercent,axis=1 ) 
    dfm['DeltaP50Percent']=dfm.apply(PPComparator.deltaP50Percent,axis=1 ) 
    dfm['DeltaP95Percent']=dfm.apply(PPComparator.deltaP95Percent,axis=1 ) 
    filter=False
    if filter :
      dfm=dfm[(dfm['count_x'] > self.p['autofocuscount']) & (dfm['count_y'] > self.p['autofocuscount']) ]
      dfm=dfm[(dfm['mean_x'] > self.p['autofocusmean']) & (dfm['mean_y'] > self.p['autofocusmean']) ]
      dfm=dfm[(abs(dfm['DeltaCountPercent']) > 10)]
    logging.warning(dfm)
    if dfm.size == 0 :
      return
    with pd.option_context('display.max_rows', None) :
      self.p['out'].h2("Comparison of requests")
      self.p['out'].out("Compare",dfm[['count_x','count_y','DeltaCount','DeltaCountPercent',
          'mean_x','mean_y','DeltaMean','DeltaMeanPercent',
          '50%_x','50%_y','DeltaP50','DeltaP50Percent',
          '95%_x','95%_y','DeltaP95','DeltaP95Percent']],
          False)

#--------------------------------------------------------------------------------------
class PPCompareProcessor() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.param=param
    self.p=self.param.getAll()
    self.p['out'].h1('PPCompareProcessor compare ' + self.p['file1'] + ' and ' + self.p['file2'])
    self.df1=PPFramor(self.param,self.p['file1']).getRawdatas()
    self.df2=PPFramor(self.param,self.p['file2']).getRawdatas()

  #--------------------------------------------------------------------------------------
  def setBehavior(self) :
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    self.percentiles=[.50,.95,.99]
    pd.options.display.float_format = '{:.0f}'.format

  #--------------------------------------------------------------------------------------
  def go(self) :
    PPComparator(self.param,self.df1,self.df2)

