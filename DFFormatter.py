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
    self.out=p['out']
    self.decimal=p['decimal']
    self.ppregex=p['ppregex']
    with open(self.fconf, 'r') as j:
      json_data = json.load(j)
      self.coalesce=json_data['COALESCE']
      self.autofocus=[]
      self.focus=json_data['FOCUS']
      self.ppalias=json_data['PPALIAS']
      self.dropcolumns=json_data['DROPCOLUMNS']
      self.droprows=json_data['DROPROWS']
      self.renamecolumns=json_data['RENAMECOLUMNS']
      logging.warning(json_data)

    self.df=None
    pd.set_option("display.max_rows",None)
    if self.file.endswith('.pan') :
      self.decimal='.'
      self.getRawdatas(False)
    else :
      self.getRawdatas(True)
    logging.warning("DFFormatter ends")

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
  def getDf(self) :
    return(self.df)

  #--------------------------------------------------------------------------------------
  def getFocusedPurepaths(self) :
    #logging.warning("focus")
    #logging.warning(self.focus)
    #logging.warning("autofocus")
    #logging.warning(self.autofocus)
    return(self.focus + self.autofocus)

  #--------------------------------------------------------------------------------------
  def setAutofocus(self,autofocus) :
    self.autofocus=autofocus
    #logging.warning("autofocus")
    #logging.warning(self.autofocus)

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
    #pd.set_option("display.max_rows",None)
    #pd.set_option("display.max_rows",10)
    self.out.h1("Analyzing file " + self.file)
    self.out.h2("Raw datas")
    rawdatas=pd.read_csv(self.file,sep=';',decimal=self.decimal)
    self.out.out("File HEAD",rawdatas.head(2))
    
    if wrangle :
      logging.warning("Wrangling file " + self.file)
      logging.warning("dropcolumns " + str(self.dropcolumns))
      rawdatas.drop (
        self.dropcolumns,
        inplace=True,axis=1
      )   
      logging.warning("renamecolumns " + str(self.renamecolumns))
      rawdatas.rename (self.renamecolumns,
        inplace=True,axis=1)
      self.out.out("File statistics before wrangle",rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
      for pp in self.droprows :
        rawdatas=rawdatas[rawdatas.PurePath.str.contains(pp)==False]
      logging.warning(rawdatas.head())
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.coalesceUrl)
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.renamePP)
      rawdatas['ts1m']=rawdatas.apply(lambda x: x['StartTime'].floor('1min'),axis=1)
      rawdatas['ts10m']=rawdatas.apply(lambda x: x['StartTime'].floor('10min'),axis=1)
      rawdatas['ts1h']=rawdatas.apply(lambda x: x['StartTime'].floor('1h'),axis=1)
      rawdatas['Error']=rawdatas.apply(lambda x: 0 if x['ErrorState'] == 'OK' else 1,axis=1)
      rawdatas.to_csv(self.file + '.pan',sep=';',index=False)
      self.out.out("File header and PP name reformatted",rawdatas.head())
      self.out.out("File statistics after wrangle",rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
    else :
      self.out.out("File statistics of .pan file",rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['ts1m']=pd.to_datetime(rawdatas['ts1m'],infer_datetime_format=True)
      rawdatas['ts10m']=pd.to_datetime(rawdatas['ts10m'],infer_datetime_format=True)
      rawdatas['ts1h']=pd.to_datetime(rawdatas['ts1h'],infer_datetime_format=True)
    if len(self.ppregex) > 0 :
      rawdatas=rawdatas[rawdatas['PurePath'].apply(self.regexFilter)]
      self.out.out("Dataframe TAIL",rawdatas.tail(2))
      self.out.out("Dataframe statistics after ppregex " + self.ppregex,rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
    else : 
      self.out.out("Dataframe TAIL",rawdatas.tail(2))
      self.out.out("Dataframe statistics",rawdatas['ResponseTime'].describe(percentiles=DFFormatter.percentiles).to_frame())
    self.df=rawdatas
