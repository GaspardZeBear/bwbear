import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import logging
from Outer import *
from DFFormatter import *
from Param import *

#----------------------------------------------------------------
class PandasGrapher() :

  #--------------------------------------------------------------------------------------
  def __init__(self,param) :
    self.fileCounter=0
    self.param=param
    self.p=param.getAll()
    self.nographs=self.p['nographs']

  #--------------------------------------------------------------------------------------
  def setDfall(self,dfall) :
    self.dfall=dfall

  #--------------------------------------------------------------------------------------
  def getPngFileName(self,s) :
    self.fileCounter += 1
    n=str(s).translate(None,' \'/.,:;\[]()-*#') + str(self.fileCounter) + '.png'
    #n=str(s).translate(None,' \'/.,:;\[]()-*') + '.png'
    logging.warning(n)
    return(n)

  #--------------------------------------------------------------------------------------
  def graphBasicsNew(self,title,dgbase,dgList) :
    if self.nographs :
      return

    logging.debug("graphBasics aggr=" + title)
    #plt.figure(figsize=(16,4))
    #fig, ax=plt.subplots(figsize=(16,4))
    plt.figure(figsize=(8,2))
    fig, ax=plt.subplots(figsize=(12,3))
    fig.autofmt_xdate()
    logging.debug("graphBasics setting ax")
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.set_title('fig.autofmt_xdate fixes the labels')
    ax.xaxis.set_major_formatter(mdates.DateFormatter(self.p['timeFormat']))
    ax.set_ylabel('Time ms', color='black')
    self.dfall.plot(rot=45,ax=ax,grid=True,linewidth=0)
    for dg in dgList :
      style=self.param.getGraphStyle(dg['aggr'])
      #logging.warning(dg)
      dg['dgaggr'].plot(title=title,rot=45,ax=ax,grid=True,color=style['color'],legend=True,label=dg['aggr'],linewidth=style['linewidth'])
      if dg['dgaggr'].count() < 50 :
        dg['dgaggr'].plot(title=title,rot=45,ax=ax,grid=True,legend=True,label=dg['aggr'],style=style['point'])
      if self.p['ymax'] > 0 :
        ax.set_ylim(ymin=0,ymax=self.p['ymax'])
      else :
        ax.set_ylim(ymin=0)
    #logging.debug("graphBasics setting axtwin")
    axtwin=ax.twinx()
    axtwin.set_ylabel('Count', color='lightgrey')
    dfCount=dgbase.count().reset_index()
    dfm=pd.merge_ordered(self.dfall,dfCount,left_on=self.p['timeGroupby'],right_on=self.p['timeGroupby'],how='outer')
    dfm = dfm.set_index(self.p['timeGroupby'])
    dfm.drop('StartTime',axis=1,inplace=True)
    dfm.fillna(value=0,inplace=True)

    dfm.plot(ax=axtwin,color='lightgrey',linestyle='--',legend=False,label='Count')
    axtwin.set_ylim(ymin=0)
    #logging.debug("title " + title)
    f=self.getPngFileName(str(title))
    plt.savefig(f)
    plt.close()
    self.p['out'].image(f,title)


  #--------------------------------------------------------------------------------------
  def myPlotBar(self,datas,title) :
    if self.nographs :
      return
    dc=datas.count()
    dm=datas.mean()
    if dc.empty :
      return
    if dc.size > 100 :
      return
    logging.warning(datas)
    df=dc.to_frame()
    df.rename(columns={"ResponseTime":"Count"},inplace=True)
    dfm=dm.to_frame()
    dfm.rename(columns={"ResponseTime":"Mean"},inplace=True)

    figYSize=int(dc.size/4) + 1

    fig=plt.figure(figsize=(16,figYSize))
    ax=fig.add_subplot(121)
    df.plot.barh(color='lightgrey',ax=ax,grid=True)
    ax.minorticks_on()
    ax.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
    axm=fig.add_subplot(122)
    dfm.plot.barh(color='green',ax=axm,grid=True,title=title)
    axm.minorticks_on()
    axm.xaxis.grid(True, which='minor', linestyle='-', linewidth=0.25)
    axm.get_yaxis().set_ticks([])

    f=self.getPngFileName(title)
    plt.tight_layout()
    plt.savefig(f)
    plt.close()
    self.p['out'].image(f,title)

