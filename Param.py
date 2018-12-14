import logging
import json
from Outer import *


class Param() :

  def __init__(self) :
    self.p={}

  def set(self,key,value) :
    self.p[key]=value

  def get(self,key) :
    return(self.p[key])

  def getAll(self) :
    return(self.p)
