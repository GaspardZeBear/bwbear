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
class PPStator() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param,df) :
    self.df=df
    self.param=param
    self.p=self.param.getAll()
    self.ppDg=self.df.groupby('PurePath')['ResponseTime'].describe(percentiles=self.p['percentiles'])
    logging.warning(self.ppDg)
    self.setThrudf()

#--------------------------------------------------------------------------------------
  def setThrudf(self) :
    self.thrudf=self.df.groupby('PurePath')['StartTime'].agg(['min','max','count']).reset_index()
    #self.thrudf['thru']=self.thrudf.apply(lambda x: (x['max']-x['min'])/x['count'],axis=1)
    self.thrudf['duration']=self.thrudf['max']-self.thrudf['min']
    self.thrudf['durationSec']=self.thrudf['duration']/np.timedelta64(1,'s')
    self.thrudf['durationMin']=self.thrudf['duration']/np.timedelta64(1,'m')
    #self.thrudf['thruSec']=self.thrudf.apply(lambda x: x['count']/x['durationSec'],axis=1)
    self.thrudf['thruSec']=self.thrudf.apply(lambda x:  x['count']/x['durationSec'] if x['durationSec'] else 0,axis=1)
    #self.thrudf['thruMin']=self.thrudf.apply(lambda x:  x['count']/x['durationMin'] if x['durationMin'] else 0,axis=1)
    self.thrudf['thruMin']=self.thrudf['thruSec']*60

    self.thruDuration=self.df['StartTime'].max() - self.df['StartTime'].min()
    self.thruDurationSec=self.thruDuration/np.timedelta64(1,'s')
    self.thruDurationMin=self.thruDuration/np.timedelta64(1,'m')
    #self.thruSec=( (self.df['StartTime'].max() - self.df['StartTime'].min())/np.timedelta64(1,'s') / self.df['StartTime'].count() )
    self.thruSec= self.df['StartTime'].count()/self.thruDurationSec if self.thruDurationSec else 0
    self.thruMin=self.thruSec*60
    logging.warning(self.thrudf)
    logging.warning(self.thruSec)

    self.xstats=pd.merge(self.ppDg,self.thrudf,on='PurePath')
    self.xstats.drop (
        ['count_x','durationMin'],
        inplace=True,axis=1
      )

#--------------------------------------------------------------------------------------
  def getXstats(self) :
    return(self.xstats)




