import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
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
  def __init__(self,f,out) :
    self.file=f
    self.out=out
    self.df=None
    pd.set_option("display.max_rows",None)
    if self.file.endswith('.pan') :
      self.getRawdatas(False)
    else :
      self.getRawdatas(True)

  def getDf(self) :
    return(self.df)

  #--------------------------------------------------------------------------------------
  def coalesceUrl(self,u) :
    if ( "list.remittancegrid.show" in u ) :
      return("*remittancegrid.show")
    if ( "login.loginform;jsessionid" in u ) :
      return("*login.loginform;jsessionid")
    if ( "list.transactiongrid" in u ) :
      return("*list.transactiongrid")
    if ( "transaction" in u ) :
      return("*transaction")
    if ( "remittance" in u ) :
      return("*remittance")
    if ( "generator" in u ) :
      return("*generator")
    if ( "merchantmanagement" in u ) :
      return("*merchantmanagement")
    return(u)

#--------------------------------------------------------------------------------------
  def renamePP(self,u) :
    if ( u in DFFormatter.PP ) :
      return(DFFormatter.PP[u])
    return(u)


#--------------------------------------------------------------------------------------
  def getRawdatas(self,wrangle=True) :
    #pd.set_option("display.max_rows",None)
  #pd.set_option("display.max_rows",10)
    self.out.h1("Analyzing file " + self.file)
    rawdatas=pd.read_csv(self.file,sep=';')
    self.out.h2("Raw datas")
    self.out.out("File HEAD",rawdatas.head())
    self.out.out("File TAIL",rawdatas.tail())
    if wrangle :
      rawdatas.drop (
        ["Breakdown","Size","Top Findings","Duration [ms]"],
        inplace=True,axis=1
      )   
      rawdatas.rename ({
        "Error State" : "ErrorState",
        "PurePath" : "PurePath",
        "Response Time [ms]" : "ResponseTime",
        "Start Time" : "StartTime"
      },inplace=True,axis=1)
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.coalesceUrl)
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      rawdatas['PurePath']=rawdatas['PurePath'].map(self.renamePP)
      rawdatas['ts1m']=rawdatas.apply(lambda x: x['StartTime'].floor('1min'),axis=1)
      rawdatas['ts10m']=rawdatas.apply(lambda x: x['StartTime'].floor('10min'),axis=1)
      rawdatas['Error']=rawdatas.apply(lambda x: 0 if x['ErrorState'] == 'OK' else 1,axis=1)
      rawdatas.to_csv(self.file + '.pan',sep=';')
      self.out.out("File header and PP name reformatted",rawdatas.head())
    self.out.out("File statistics",rawdatas.describe(percentiles=DFFormatter.percentiles))
    self.df=rawdatas
