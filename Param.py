import logging
import json
from Outer import *


class Param() :

  graphStyles={
    "Mean" : { "color": "green", "linewidth" :2 , "point" : "go"},
    "Q50" : { "color": "green", "linewidth" :0.2 , "point" : "g-"},
    "Q95" : { "color": "yellow", "linewidth" :0.2 , "point" : "y+"},
    "Max" : { "color": "red", "linewidth" :0.2 , "point" : "ro"},
    "default" : { "color": "black", "linewidth" :1 , "point" : "go"}
  }
    

  def __init__(self) :
    self.p={}

  def set(self,key,value) :
    self.p[key]=value

  def get(self,key) :
    return(self.p[key])

  def getGraphStyle(self,key) :
    if key in Param.graphStyles :
      return(Param.graphStyles[key])
    else :
      return(Param.graphStyles["default"])

  def getAll(self) :
    return(self.p)

  def processParam(self) :
    if 'verbose' in self.p and self.p['verbose'] :
      logging.basicConfig(format="%(asctime)s f=%(funcName)s %(levelname)s %(message)s", level=logging.DEBUG)
    else :
      logging.basicConfig(format="%(asctime)s f=%(funcName)s %(levelname)s %(message)s", level=logging.WARNING)
    logging.warning("Logging initialized")
    if 'output' in self.p :
      if self.p['output'] ==  'html' :
        self.p['out']=OutputHtml()
      else :
        self.p['out']=OutputTty()
    else :
        self.p['out']=OutputTty()
    self.p['out'].open()
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
    if 'ppregexclude' not in self.p :
      self.p['ppregexclude']=''


