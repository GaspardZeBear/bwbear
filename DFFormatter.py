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

  COALESCE_DMP = [
    ".png",
    "/dmp/documents/liste:seedoc",
    "/dmp/recapitulatif:consultdocument/",
    "/mobilegateway/rest/Document/",
    "/dmp/documents/liste.lignedeviecomponent:linktooltip",
    "/dmp/creation/recherchepatientparcartevitale:redirecttodmpcreation",
    "/dmp/creation/recherchepatientparcartevitale:redirecttodmpaccess/",
    "/mespatients:opendmp/",
    "/login;jsessionid",

  ]
  def __init__(self,f,fconf,out) :
    self.file=f
    self.fconf=fconf
    with open('DMP.json', 'r') as j:
      json_data = json.load(j)
      self.coalesce=json_data['COALESCE']
      self.focus=json_data['FOCUS']
      print(json_data)

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
  def coalesceUrlCasino(self,u) :
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
  def getInterestingPurepathsDmp(self) :
    return([
      "/dmp/creation/recherchepatientparcartevitale",
      "/rechercherpatient",
      "/dmp/documents/historiqueacces/raz",
      "/dmp/documents/consultationdocument",
      "/dmp/creation/donneesadministratives.formcreation",
      "/dmp/gestiondmp/telechargementtotal.telechargementform",
      "/si-dmp-server/v1/services/repository",
      "/si-dmp-server/v1/services//repository",
      "/si-dmp-server/v1/services/habilitations",
      "/si-dmp-server/v1/services/registry",
      "/si-dmp-server/v1/services/patients",
      "/si-dmp-server/v2/services/patients",
      "/si-dmp-server/v2/services/patientCertif"
      ])

  #--------------------------------------------------------------------------------------
  def getInterestingPurepaths(self) :
    #return(self.getInterestingPurepathsDmp())
    return(self.focus)

  #--------------------------------------------------------------------------------------
  def XcoalesceUrl(self,u) :
    for pat in DFFormatter.COALESCE_DMP :
      if pat in u :
        return("*" + pat)
    return(u)

  #--------------------------------------------------------------------------------------
  def coalesceUrl(self,u) :
    for pat in self.coalesce :
      if pat['pattern'] in u :
        logging.warning(u + " " + pat['pattern'])
        if len(pat['to']) > 0 :
          return(pat['to'])
        else :
          return("*"+pat['pattern'])
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
      rawdatas.to_csv(self.file + '.pan',sep=';',index=False)
      self.out.out("File header and PP name reformatted",rawdatas.head())
    else :
      rawdatas['StartTime']=pd.to_datetime(rawdatas['StartTime'],infer_datetime_format=True)
      #rawdatas.drop (
      #  ["Unnamed: 0"],
      #  inplace=True,axis=1
      #)

    self.out.out("File TAIL",rawdatas.tail())
    #self.out.out("Infos",rawdatas.info())
    self.out.out("File statistics",rawdatas.describe(percentiles=DFFormatter.percentiles))
    self.df=rawdatas
