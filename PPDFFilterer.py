import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
import re
from Outer import *
from Param import *

#----------------------------------------------------------------
class PPDFFilterer() :

  #--------------------------------------------------------------------------------------
  def __init__(self,df,param) :
    self.df=df
    self.param=param
    self.p=self.param.getAll()
    self.ppregex=self.p['ppregex']
    self.ppregexclude=self.p['ppregexclude']
    self.timeregex=self.p['timeregex']
    self.start=self.p['start']
    self.end=self.p['end']
    self.buildDataframes()
    self.filtered=0

  #--------------------------------------------------------------------------------------
  def startFilter(self,val):
    if val:
        if val >= self.start :
            return True
        else:
            return False
    else:
        return False

  #--------------------------------------------------------------------------------------
  def endFilter(self,val):
    #logging.warning(self.end + " " + val)
    if val:
        if val <= self.end :
            return True
        else:
            return False
    else:
        return False


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
  def getDfOK(self) :
    return(self.dfOK)

  #--------------------------------------------------------------------------------------
  def getDfKO(self) :
    return(self.dfKO)

  #--------------------------------------------------------------------------------------
  def getDfall(self) :
    return(self.dfall)

  #--------------------------------------------------------------------------------------
  def getDfHigh(self) :
    return(self.dfHigh)

  #--------------------------------------------------------------------------------------
  def getFiltered(self) :
    return(self.filtered)

  #--------------------------------------------------------------------------------------
  def buildDataframes(self) :
    rawdatas=self.filter()
    self.dfOK=rawdatas[ ( rawdatas['ErrorState'] == 'OK' ) ]
    self.dfKO=rawdatas[ ( rawdatas['ErrorState'] != 'OK') ]
    self.dfall=pd.DataFrame(self.dfOK.groupby(self.p['timeGroupby'])['StartTime'].count().apply(lambda x: 0))
    #self.dfFocus=self.dfOK[ self.dfOK['PurePath'].isin( self.getFocusedPurepaths()) ]
    self.dfHigh=self.dfOK[ ( self.dfOK['ResponseTime'] > self.p['highResponseTime'] ) ]


  #--------------------------------------------------------------------------------------
  def filter(self) :
    sizein=len(self.df)
    rawdatas=self.df
    if len(self.ppregex) > 0 :
      rawdatas=rawdatas[rawdatas['PurePath'].apply(self.regexFilter)]
    if len(self.ppregexclude) > 0 :
      rawdatas=rawdatas[rawdatas['PurePath'].apply(self.regexcludeFilter)]
    if len(self.timeregex) > 0 :
      logging.warning("Apply timeregex filter")
      rawdatas=rawdatas[rawdatas['StartTimeStr'].apply(self.timeregexFilter)]
    if len(self.start) > 0  :
      logging.warning("Apply start filter")
      rawdatas=rawdatas[rawdatas['StartTimeStr'].apply(self.startFilter)]
    if len(self.end) > 0  :
      logging.warning("Apply end filter")
      rawdatas=rawdatas[rawdatas['StartTimeStr'].apply(self.endFilter)]
    self.filtered=sizein - len(rawdatas.index)
    return(rawdatas)
