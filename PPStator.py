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
    self.xstats=pd.DataFrame()
    
    if len(self.df) == 0 :
      return
    if self.p['xstats'] == 0 :
      #self.xstats=self.df['ResponseTime'].describe(percentiles=self.p['percentiles'])
      logging.warning("PPStator level 0")
      return
    elif self.p['xstats'] == 1 :
      logging.warning("PPStator level 1")
      self.described=self.df.describe(percentiles=self.p['percentiles']).T
    else :
      logging.warning("PPStator level > 1")
      logging.warning(df)
      dg=self.df.groupby('PurePath')['ResponseTime']
      logging.warning("PPStator level > 1 : dg=")
      logging.warning(dg)
      self.ppDg=dg.describe(percentiles=self.p['percentiles'])
      logging.warning(self.ppDg)
      # Build a global entry for describe and concat it for 
      self.described=pd.concat([self.ppDg,self.df.describe(percentiles=self.p['percentiles']).T],axis=0)
    
    self.described=self.described.reset_index()
    self.described.replace('ResponseTime','*',inplace=True)
    self.described=self.described[ self.described['index'] != 'Error']
    self.described.rename(columns={'index':'PurePath'},inplace=True)

    #logging.warning(self.described)

    # Build a global entry for throughput
    d= { 'PurePath' : ['*'],
         'min' : [self.df['StartTime'].min()],
         'max' : [self.df['StartTime'].max()],
         'count' : [self.df['StartTime'].count()],
    #     'skew' : skew,
    }
    self.globalThru=pd.DataFrame.from_dict(d).reset_index()
    #logging.warning(self.globalThru)
    self.setThrudf()

  #--------------------------------------------------------------------------------------
  def setThrudf(self) :
    if self.p['xstats'] > 1 :
      self.thrudf0=self.df.groupby('PurePath')['StartTime'].agg(['min','max','count']).reset_index()
      self.thrudf=pd.concat([self.thrudf0,self.globalThru],axis=0)
    else :
      self.thrudf=self.globalThru
    #logging.warning(self.thrudf)

    # Compute throughput infos
    self.thrudf['duration']=self.thrudf['max']-self.thrudf['min']
    self.thrudf['durationSec']=self.thrudf['duration']/np.timedelta64(1,'s')
    self.thrudf['durationMin']=self.thrudf['duration']/np.timedelta64(1,'m')
    self.thrudf['thruSec']=self.thrudf.apply(lambda x:  x['count']/x['durationSec'] if x['durationSec'] else 0,axis=1)
    self.thrudf['thruMin']=self.thrudf['thruSec']*60

    # Merge by pure (+ global entry)
    self.xstats=pd.merge(self.described,self.thrudf,on='PurePath')
    self.xstats.drop (
        ['index','count_x','durationMin'],
        inplace=True,axis=1
      )
    self.xstats.rename(columns={'min_x':'min','max_x':'max', 'count_y':'count', 'min_y':'begin','max_y':'end'},inplace=True)
    #logging.warning(self.xstats)

#--------------------------------------------------------------------------------------
  def getXstats(self) :
    return(self.xstats)




