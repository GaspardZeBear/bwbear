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
    if self.p['xstats'] > 1 :
      self.ppDg=self.df.groupby('PurePath')['ResponseTime'].describe(percentiles=self.p['percentiles'])
      # Build a global entry for describe and concat it for 
      self.described=pd.concat([self.ppDg,self.df.describe(percentiles=self.p['percentiles']).T],axis=0)
    else :
      self.described=self.df.describe(percentiles=self.p['percentiles']).T
    
    self.described=self.described.reset_index()
    self.described.replace('ResponseTime','*',inplace=True)
    self.described=self.described[ self.described['index'] != 'Error']
    self.described.rename(columns={'index':'PurePath'},inplace=True)

    logging.warning(self.described)

    # Build a global entry for throughput
    d= { 'PurePath' : ['*'],
         'min' : [self.df['StartTime'].min()],
         'max' : [self.df['StartTime'].max()],
         'count' : [self.df['StartTime'].count()],
    #     'skew' : skew,
    }
    self.globalThru=pd.DataFrame.from_dict(d).reset_index()
    logging.warning(self.globalThru)
    self.setThrudf()

  #--------------------------------------------------------------------------------------
  def setThrudf(self) :
    if self.p['xstats'] > 1 :
      self.thrudf0=self.df.groupby('PurePath')['StartTime'].agg(['min','max','count']).reset_index()
      self.thrudf=pd.concat([self.thrudf0,self.globalThru],axis=0)
    else :
      self.thrudf=self.globalThru
    logging.warning(self.thrudf)

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
    logging.warning(self.xstats)

#--------------------------------------------------------------------------------------
  def getXstats(self) :
    return(self.xstats)




