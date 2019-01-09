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
  def __init__(self,p) :
    logging.warning("DFFormatter begins")
    self.file=p['datafile']
    self.fconf=p['formatfile']
    self.decimal=p['decimal']
    self.infos=dict()
    self.infos['Datafile']=self.file
    self.infos['DescribeInitial']=None
    self.infos['DescribeFinal']=None
    self.infos['HeadInitial']=None
    self.infos['HeadFinal']=None
    self.wrangle=False
    with open(self.fconf, 'r') as j:
      self.json = json.load(j)
      self.infos['json']=self.json
      self.coalesce=self.json['COALESCE']
      self.autofocus=[]
      self.focus=self.json['FOCUS']
      self.ppalias=self.json['PPALIAS']
      self.dropcolumns=self.json['DROPCOLUMNS']
      self.droprows=self.json['DROPROWS']
      self.renamecolumns=self.json['RENAMECOLUMNS']
      logging.warning(self.json)

    self.df=None
    pd.set_option("display.max_rows",None)
    if self.file.endswith('.pan') :
      self.decimal='.'
      self.getRawdatas(False)
    else :
      self.getRawdatas(True)
    logging.warning("DFFormatter ends")

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
  def getRawdatas(self,wrangle=True) :
    rawdatas=pd.read_csv(self.file,sep=';',decimal=self.decimal)
    self.infos['HeadInitial']=rawdatas.head(2)
    self.infos['TailInitial']=rawdatas.tail(2)
    
    if wrangle :
      self.wrangle=True
      logging.warning("Wrangling file " + self.file)
      logging.warning("dropcolumns " + str(self.dropcolumns))
      rawdatas.drop (
        self.dropcolumns,
        inplace=True,axis=1
      )   
      logging.warning("renamecolumns " + str(self.renamecolumns))
      rawdatas.rename (self.renamecolumns,
        inplace=True,axis=1)
      self.infos['DescribeInitial']=rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame()
      for pp in self.droprows :
        rawdatas=rawdatas[rawdatas.PurePath.str.contains(pp)==False]
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
