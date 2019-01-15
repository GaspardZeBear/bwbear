import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
import json
import re
from Outer import *


class DFFormatter() :

  percentiles=[.50,.95,.99]
  pd.options.display.float_format = '{:.0f}'.format

  #--------------------------------------------------------------------------------------
  @staticmethod
  def getFromFactory(type,params) :
    if type == 'dynatrace' :
      return(DFFormatterDynatrace(params))
    else :
      return(DFFormatterJmeter(params))

  #--------------------------------------------------------------------------------------
  def __init__(self,p) :
    logging.warning("DFFormatter begins")
    logging.warning("scriptpath : " + p['scriptpath'])
    self.p=p
    self.file=p['datafile']
    self.fconf=''
    self.decimal=p['decimal']
    self.infos=dict()
    self.infos['Datafile']=self.file
    self.infos['DescribeInitial']=None
    self.infos['DescribeFinal']=None
    self.infos['HeadInitial']=None
    self.infos['HeadFinal']=None
    self.wrangle=False
    self.df=None
    pd.set_option("display.max_rows",None)
    if self.file.endswith('.pan') :
      self.decimal='.'
      self.formatDf(False)
    else :
      self.fconf=p['formatfile']
      self.processFormatFile()
      self.formatDf(True)
    logging.warning("DFFormatter ends")

  #--------------------------------------------------------------------------------------
  def processFormatFile(self) :
    with open(self.fconf, 'r') as j:
      self.json = json.load(j)
      self.infos['json']=self.json
      self.coalesce=self.json['COALESCE']
      self.autofocus=[]
      self.focus=self.json['FOCUS']
      self.ppalias=self.json['PPALIAS']
      #self.dropcolumns=self.json['DROPCOLUMNS']
      self.droprows=self.json['DROPROWS']
      #self.renamecolumns=self.json['RENAMECOLUMNS']
      logging.warning(self.json)

  #--------------------------------------------------------------------------------------
  def getDf(self) :
    return(self.df)

  #--------------------------------------------------------------------------------------
  def isWrangled(self) :
    return(self.wrangle)

  #--------------------------------------------------------------------------------------
  def getInfos(self,info) :
    if info in self.infos :
      return(self.infos[info])
    return

  #--------------------------------------------------------------------------------------
  def coalesceUrl(self,u) :
    for pat in self.coalesce.keys() :
      if pat in u :
        #logging.warning(u + " " + pat)
        if len(self.coalesce[pat] ) > 0 :
          return("*" + self.coalesce[pat])
        else :
          return("*"+pat)
    return(u)

  #--------------------------------------------------------------------------------------
  def renamePP(self,u) :
    if ( u in self.ppalias ) :
      return(self.ppalias[u])
    return(u)

  #--------------------------------------------------------------------------------------
  def getColumnsToProcess(self,f) :
    with open(self.p['scriptpath']+"/"+f, 'r') as j:
      self.json = json.load(j)
      self.dropcolumns=self.json['DROPCOLUMNS']
      #[str(x) for x in self.dropcolumns]
      self.renamecolumns=self.json['RENAMECOLUMNS']

  #--------------------------------------------------------------------------------------
  def preProcess(self,df) :
    return(df)

  #--------------------------------------------------------------------------------------
  def getRawdatas(self,wrangle=True) :
    rawdatas=pd.read_csv(self.file,sep=';',decimal=self.decimal)
    logging.warning(rawdatas.dtypes)
    self.infos['HeadInitial']=rawdatas.head(2)
    self.infos['TailInitial']=rawdatas.tail(2)
    logging.warning("Head initial")
    logging.warning(self.infos['HeadInitial'])

    if wrangle :
      self.wrangle=True
      logging.warning("Wrangling file " + self.file)
      rawdatas.drop (
        self.dropcolumns,
        inplace=True,axis=1
      )
      rawdatas.rename (self.renamecolumns,
        inplace=True,axis=1)
      self.infos['DescribeInitial']=rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame()

      logging.warning("Before preProcess")
      logging.warning(rawdatas.head())
      rawdatas=self.preProcess(rawdatas) 
      logging.warning("After preProcess")
      logging.warning(rawdatas.head())

      for pp in self.droprows :
        rawdatas=rawdatas[rawdatas.PurePath.str.contains(pp)==False]
      logging.warning("After dropRows")
      logging.warning(rawdatas.head())
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.coalesceUrl)
      rawdatas['StartTimeStr']=rawdatas['StartTime']
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.renamePP)
      rawdatas['ts1m']=rawdatas.apply(lambda x: x['StartTime'].floor('1min'),axis=1)
      rawdatas['ts10m']=rawdatas.apply(lambda x: x['StartTime'].floor('10min'),axis=1)
      rawdatas['ts1h']=rawdatas.apply(lambda x: x['StartTime'].floor('1h'),axis=1)
      rawdatas['Error']=rawdatas.apply(lambda x: 0 if x['ErrorState'] == 'OK' else 1,axis=1)
      rawdatas.to_csv(self.file + '.pan',sep=';',index=False)
      logging.warning("Ready ")
      logging.warning(rawdatas.head())
    else :
      self.infos['DescribeInitial']=rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame()
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['ts1m']=pd.to_datetime(rawdatas['ts1m'],infer_datetime_format=True)
      rawdatas['ts10m']=pd.to_datetime(rawdatas['ts10m'],infer_datetime_format=True)
      rawdatas['ts1h']=pd.to_datetime(rawdatas['ts1h'],infer_datetime_format=True)
    self.infos['DescribeFinal']=rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame()
    self.infos['HeadFinal']=rawdatas.head(2)
    self.infos['TailFinal']=rawdatas.tail(2)
    self.df=rawdatas

#--------------------------------------------------------------------------------------
class DFFormatterDynatrace(DFFormatter) :
#--------------------------------------------------------------------------------------
  def formatDf(self,wrangle=True) :
    self.getColumnsToProcess('dynatrace.json')  
    self.getRawdatas(wrangle)

#--------------------------------------------------------------------------------------
class DFFormatterJmeter(DFFormatter) :
#--------------------------------------------------------------------------------------

  #--------------------------------------------------------------------------------------
  def preProcess(self,df) :
    logging.warning(df.head(5))
    df['StartTime']=pd.to_datetime(df['StartTime'],unit='ms')
    logging.warning(df.head(5))
    df['ErrorState']=df.apply(lambda x: 'OK' if x['ErrorState'] else 'KO',axis=1)
    df['Agent']="_agent"
    df['Application']="_application"
    return(df)

  #--------------------------------------------------------------------------------------
  def formatDf(self,wrangle=True) :
    self.getColumnsToProcess('jmeter.json')  
    logging.warning(wrangle)
    self.getRawdatas(wrangle)
    


