import logging
import json
from Outer import *
import os
import sys

#---------------------------------------------------------------------------------------------------
class Param() :

  graphStyles={
    "Mean" : { "color": "green", "linewidth" :2 , "point" : "go"},
    "Q50" : { "color": "cyan", "linewidth" :0.2 , "point" : "g-"},
    "Q95" : { "color": "yellow", "linewidth" :0.2 , "point" : "y+"},
    "Max" : { "color": "red", "linewidth" :0.2 , "point" : "ro"},
    "default" : { "color": "black", "linewidth" :1 , "point" : "go"}
  }

  #---------------------------------------------------------------------------------------------------
  def __init__(self) :
    self.p={}

  #---------------------------------------------------------------------------------------------------
  def set(self,key,value) :
    self.p[key]=value

  #---------------------------------------------------------------------------------------------------
  def get(self,key) :
    return(self.p[key])

  #---------------------------------------------------------------------------------------------------
  def getGraphStyle(self,key) :
    if key in Param.graphStyles :
      return(Param.graphStyles[key])
    else :
      return(Param.graphStyles["default"])

  #---------------------------------------------------------------------------------------------------
  def getAll(self) :
    return(self.p)

  #---------------------------------------------------------------------------------------------------
  def getAllAsString(self) :
    s=''
    for k in self.p :
      s += " --" + k + " " + str(self.p[k])
    return(s)

  #---------------------------------------------------------------------------------------------------
  def processParam(self) :
    self.p['scriptpath']=os.path.abspath(os.path.dirname(sys.argv[0]))
    if 'verbose' in self.p and self.p['verbose'] :
      logging.basicConfig(format="%(asctime)s f=%(funcName)s %(levelname)s %(message)s", level=logging.DEBUG)
    else :
      logging.basicConfig(format="%(asctime)s f=%(funcName)s %(levelname)s %(message)s", level=logging.WARNING)

    logging.warning("Logging initialized")
    if 'quick' not in self.p :
      self.p['quick'] = False
    if 'nodescribe' not in self.p :
      self.p['nodescribe'] = False
    if 'nobuckets' not in self.p :
      self.p['nobuckets'] = False
    if 'nographs' not in self.p :
      self.p['nographs'] = False
    if 'output' in self.p :
      if self.p['output'] ==  'html' :
        logging.warning("Output HTML")
        self.p['out']=OutputHtml()
      else :
        logging.warning("Output TTy")
        self.p['out']=OutputTty()
    else :
        logging.warning("Default Output TTy")
        self.p['out']=OutputTty()
    self.p['out'].open()
    if 'buckets' not in self.p :
      self.p['buckets']=[0,100,200,300,400,500,1000,2000,3000,4000,5000,10000,20000,30000,60000,1000000]
    else :
      self.p['buckets']=[int(s) for s in self.p['buckets'].split(',')]

    if 'steps' not in self.p or len(self.p['steps']) == 0 :
      self.p['steps']=[
      'Formatfile',
      'Params',
      'Stats',
      'File',
      'OK',
      'KO',
      'Focus',
      'HighResponseTime',
      'KODetails',
      ]
    else :
      self.p['steps']=[s for s in self.p['steps'].split(',')]

    if 'datafile' not in self.p :
      self.p['datafile']=''
    if 'workdir' not in self.p :
      self.p['workdir']=self.p['datafile'] + '.workdir'

    if 'type' not in self.p :
      self.p['type']='dynatrace'
    if 'decimal' not in self.p :
      self.p['decimal']=','
    if 'ymax' not in self.p :
      self.p['ymax']='0'
    if 'timeGroupby' not in self.p :
      self.p['timeGroupby']='ts1m'
    if 'timeFormat' not in self.p :
      self.p['timeFormat']='%H-%M'
    if 'highResponseTime' not in self.p :
      self.p['highResponseTime']=5000
    if 'autofocusmean' not in self.p :
      self.p['autofocusmean']=500
    if 'autofocuscount' not in self.p :
      self.p['autofocuscount']=30
    if 'ppregex' not in self.p :
      self.p['ppregex']=''
    if 'timeregex' not in self.p :
      self.p['timeregex']=''
    if 'ppregexclude' not in self.p :
      self.p['ppregexclude']=''


