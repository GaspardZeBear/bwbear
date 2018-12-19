import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
import json
from Outer import *


class DFFormatter() :

  percentiles=[.50,.95,.99]
  pd.options.display.float_format = '{:.0f}'.format


  PP={
      "Go to page result 5" : "Result5",
      "Go to remise detail" : "RemiseDetail",
      "Go to remises tab" : "RemiseTab",
      "Go to transaction detail" : "TransactionDetail",
      "Search remises on Date" : "SearchRemisesDate",
      "Search transactions on Date" : "SearchTransactionsDate",
      "Search transactions on Date & paymentScheme" : "SearchTransactionsDateScheme",
  }

  #--------------------------------------------------------------------------------------
  def __init__(self,f,fconf,out) :
    self.file=f
    self.fconf=fconf
    with open(self.fconf, 'r') as j:
      json_data = json.load(j)
      self.coalesce=json_data['COALESCE']
      self.autofocus=[]
      self.focus=json_data['FOCUS']
      self.ppalias=json_data['PPALIAS']
      self.dropcolumns=json_data['DROPCOLUMNS']
      self.renamecolumns=json_data['RENAMECOLUMNS']
      logging.warning(json_data)

    self.out=out
    self.df=None
    pd.set_option("display.max_rows",None)
    if self.file.endswith('.pan') :
      self.getRawdatas(False)
    else :
      self.getRawdatas(True)

  #--------------------------------------------------------------------------------------
  def getDf(self) :
    return(self.df)

  #--------------------------------------------------------------------------------------
  def getFocusedPurepaths(self) :
    logging.warning("focus")
    logging.warning(self.focus)
    logging.warning("autofocus")
    logging.warning(self.autofocus)
    return(self.focus + self.autofocus)

  #--------------------------------------------------------------------------------------
  def setAutofocus(self,autofocus) :
    self.autofocus=autofocus
    logging.warning("autofocus")
    logging.warning(self.autofocus)

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
    rawdatas=pd.read_csv(self.file,sep=';')
    self.out.h2("Raw datas")
    self.out.out("File HEAD",rawdatas.head())
    
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
      logging.warning(rawdatas.head())
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.coalesceUrl)
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.renamePP)
      rawdatas['ts1m']=rawdatas.apply(lambda x: x['StartTime'].floor('1min'),axis=1)
      rawdatas['ts10m']=rawdatas.apply(lambda x: x['StartTime'].floor('10min'),axis=1)
      rawdatas['Error']=rawdatas.apply(lambda x: 0 if x['ErrorState'] == 'OK' else 1,axis=1)
      rawdatas.to_csv(self.file + '.pan',sep=';',index=False)
      self.out.out("File header and PP name reformatted",rawdatas.head())
    else :
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['ts1m']=pd.to_datetime(rawdatas['ts1m'],infer_datetime_format=True)
      rawdatas['ts10m']=pd.to_datetime(rawdatas['ts10m'],infer_datetime_format=True)
      #rawdatas.drop (
      #  ["Unnamed: 0"],
      #  inplace=True,axis=1
      #)
    logging.warning(rawdatas.dtypes)
    self.out.out("File TAIL",rawdatas.tail())
    #self.out.out("Infos",rawdatas.info())
    self.out.out("File statistics",rawdatas.describe(percentiles=DFFormatter.percentiles))
    self.df=rawdatas
