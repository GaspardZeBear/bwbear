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
class SQLFramor() :

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
    logging.warning("DFFormatter begins")
    self.file=file
    self.decimal=','
    self.remove={"Database and Connection Pool":"Sql","Acqu Time/Trans [ms]":"AcqTime","Executions/Trans":"ExecPerTrans",
      "Exec Total [ms]":"ExecTotal","Exec Avg [ms]":"ExecAvg","Exec Max [ms]":"ExecMax","Exec Min [ms]":"ExecMin","Executions": "ExecCount",
      "Failed %":"PFailed","Round trips":"RT"}
    self.drop=["ExecPerTrans","RT"]
    SQLFramor.fileNum += 1
    SQLFramor.databaseNum  = 0 
    SQLFramor.sqlNum  = 0 
    self.setRawdatas()
    logging.warning("DFFormatter ends")

  @staticmethod
  def setSqlId(row) :
    if row['Level'] == 1 :
      SQLFramor.databaseNum += 1
      SQLFramor.sqlNum = 1
    else :
      SQLFramor.sqlNum += 1
    return(str(SQLFramor.fileNum) + "." + str(SQLFramor.databaseNum) + "." + str(SQLFramor.sqlNum) ) 

  @staticmethod
  def setDatabase(row) :
    if row['Level'] == 1 :
      SQLFramor.database = row['Sql']
    return(SQLFramor.database)


#--------------------------------------------------------------------------------------
  def getRawdatas(self) :
    return(self.rawdatas)

#--------------------------------------------------------------------------------------
  def setRawdatas(self) :
    self.rawdatas=pd.read_csv(self.file,sep=';',decimal=self.decimal)
    self.rawdatas.rename(self.remove,inplace=True,axis=1)
    self.rawdatas.drop(self.drop,inplace=True,axis=1)
    self.rawdatas['SqlId']=self.rawdatas.apply(SQLFramor.setSqlId,axis=1 )
    self.rawdatas['Database']=self.rawdatas.apply(SQLFramor.setDatabase,axis=1 )
    self.rawdatas['Lnk']=self.rawdatas.apply(lambda x: "<div id=\"" + x['SqlId'] + "\">" + x['SqlId'] + "</div>" ,axis=1 )
    self.rawdatas['ASql']=self.rawdatas.apply(lambda x: "<div style=\"text-align:left\">" + x['Sql'] + "</div>" ,axis=1 )
    #print(self.rawdatas.dtypes)
    self.rawdatas['SqlHash']=self.rawdatas.apply( lambda x: hashlib.md5(x['Sql']).hexdigest(),axis=1 )
    #print(self.rawdatas.head())
    self.p['out'].h2("SQL requests from " + self.file)
    with pd.option_context('display.max_rows', None, 'display.max_colwidth', 0) :
      self.p['out'].out("SQL",self.rawdatas[['Lnk','ASql']],False)

#--------------------------------------------------------------------------------------
class SQLComparator() :

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
    if x['ExecCount_x'] > 0 :
      return(100*(x['ExecCount_y']-x['ExecCount_x'])/x['ExecCount_x'])
    return(0)

  #--------------------------------------------------------------------------------------
  def go(self) :
    dfm=pd.merge(self.df1,self.df2,on='SqlHash',how='outer')
    dfm.fillna(0)
    dfm['DeltaCount']=dfm.apply(lambda x: x['ExecCount_y'] - x['ExecCount_x'],axis=1 ) 
    dfm['DeltaCountPercent']=dfm.apply(SQLComparator.deltaCountPercent,axis=1 ) 
    dfm=dfm[(dfm['ExecCount_x'] > self.p['autofocuscount']) & (dfm['ExecCount_y'] > self.p['autofocuscount']) ]
    dfm=dfm[(dfm['ExecAvg_x'] > self.p['autofocusmean']) & (dfm['ExecAvg_y'] > self.p['autofocusmean']) ]
    dfm=dfm[(abs(dfm['DeltaCountPercent']) > 10)]
    if dfm.size == 0 :
      return
    dfm['xLnk']=dfm.apply(lambda x: "<a href=\"#" + str(x['SqlId_x']) + "\">" + str(x['SqlId_x']) + "</a>" ,axis=1 )
    dfm['yLnk']=dfm.apply(lambda x: "<a href=\"#" + str(x['SqlId_y']) + "\">" + str(x['SqlId_y']) + "</a>" ,axis=1 )
    self.p['out'].h2("Comparison of requests")
    with pd.option_context('display.max_rows', None) :
      self.p['out'].out("Compare",dfm[['xLnk','Sql_x','yLnk','Sql_y','ExecCount_x','ExecCount_y','DeltaCount','DeltaCountPercent','ExecAvg_x','ExecAvg_y']],False)


#--------------------------------------------------------------------------------------
class SQLProcessor() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.param=param
    self.p=self.param.getAll()
    self.df1=SQLFramor(self.param,self.p['file1']).getRawdatas()
    self.df2=SQLFramor(self.param,self.p['file2']).getRawdatas()

  #--------------------------------------------------------------------------------------
  def setBehavior(self) :
    self.sqlregex=self.p['sqlregex']
    self.sqlregexclude=self.p['sqlregexclude']
    self.percentiles=[.50,.95,.99]
    pd.options.display.float_format = '{:.0f}'.format

  #--------------------------------------------------------------------------------------
  def go(self) :
    SQLComparator(self.param,self.df1,self.df2)

