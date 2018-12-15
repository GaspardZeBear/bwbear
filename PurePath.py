import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#ErrorState;PurePath;ResponseTime;Agent;Application;StartTime
#OK;/casino/fr/transaction/list;11236.98926;11321;centralreport-casino-vindemia.aw.atos.net;2018-11-14 05:59:57;
#OK;/casino/fr/transaction/list;9426.301758;11321;centralreport-casino-vindemia.aw.atos.net;2018-11-14 06:00:00;
#OK;/casino/;400.1700439;11321;centralreport-casino-hyper-super.aw.atos.net;2018-11-14 06:00:01;

percentiles=[.50,.95,.99]
pd.options.display.float_format = '{:.0f}'.format

#--------------------------------------------------------------------------------------
class Out() :

  def open(self) :
    pass 
  def close(self) :
    pass 
  def image(self,img) :
    pass 

#--------------------------------------------------------------------------------------
class OutputHtml(Out) :

  def open(self) :
    print("<html>")
    print("<body>")

  def close(self) :
    print("</body>")
    print("</html>")

  def out(self,title,o) :
    print("<h2>"+title+"</h2>")
    print(o.to_html())

  def image(self,img) :
    print("<img src=\"" +img+ "\">")

#--------------------------------------------------------------------------------------
class OutputTty(Out) :

  def out(self,title,o) :
    print("----------------------------------------------------------------")
    print(title)
    print(o)

#--------------------------------------------------------------------------------------
def bucket(x) :
  return(x)

#--------------------------------------------------------------------------------------
def coalesceUrl(u) :
  if ( "/casino/fr/remittance/list.remittancegrid.show" in u ) :
    return("*remittancegrid.show")
  if ( "login.loginform#jsessionid" in u ) :
    return("*login.loginform#jsessionid")
  if ( "list.transactiongrid" in u ) :
    return("*list.transactiongrid")
  return(u)
  
#--------------------------------------------------------------------------------------
def getRawdatas(f='datas.pan') :
  pd.set_option("display.max_rows",None)
  #pd.set_option("display.max_rows",10)
  rawdatas=pd.read_csv(f,sep=';')
  OUT.out("--> rawdatas",rawdatas.describe(percentiles=percentiles))
  return(rawdatas)

#--------------------------------------------------------------------------------------
def statsOnKO(datas) :
  kodatas=datas[datas.ErrorState.str.contains("KO")]
  OUT.out("--> datas with RC ko",kodatas.describe(percentiles=percentiles))

#--------------------------------------------------------------------------------------
def statsOnOK(datas) :
  odatas=datas[datas['ErrorState'].str.contains("OK")]
  OUT.out("--> datas with RC ok",odatas.describe(percentiles=percentiles))

#--------------------------------------------------------------------------------------
def removeAssets(datas) :
  odatas=datas[datas.PurePath.str.contains("assets")==False]
  return(odatas)


#print("datas bucketted ")
#def bucketize(u) :
#  x=int(u/1000)
#print(datas['ResponseTime'])
#datas['bucket']=round(datas['ResponseTime'])
#datas['bucket']=datas.apply(lambda row: round(datas['ResponseTime']), axis=1)
#datas['bucket']=datas.apply(lambda row: round(row.ResponseTime/1000), axis=1)
#datas['bucketMax']=datas.apply(lambda row: min([10,round(row.ResponseTime/1000)]), axis=1)
#print(datas)

#--------------------------------------------------------------------------------------
def myPlot(datas) :
  ResponseTime=datas['ResponseTime']
  #print(ResponseTime)
  datas.plot.bar()
  ResponseTime.plot.bar()
  #plt.show()
  #ResponseTime.plot.hist()
  plt.savefig('toto1.png')
  OUT.image('toto1.png')

#--------------------------------------------------------------------------------------
def highValues(datas,threshold) :
  high=datas[ datas['ResponseTime']>threshold ]
  #OUT.out("High Resp",high)
  return(high)

#--------------------------------------------------------------------------------------
def groupBy(datas,grps) :
  dg=datas.groupby(grps)
  OUT.out("GroupBy " + str(grps),dg.describe(percentiles=percentiles))
  return(dg)

#--------------------------------------------------------------------------------------
def compareHh(datas) :
  #df7=datas[ (datas['Hh'] == 7) & (datas['PurePath'] == '/cos/fr/login') ]
  #df7=datas[ (datas['Hh'] == 7) ]
  #df8=datas[ (datas['Hh'] == 8) & (datas['PurePath'] == '/cos/fr/login') ]
  #OUT.out("compare ",df7 )
  #df7mean=df7['ResponseTime'].groupby([df7['PurePath'],df7['Application']]).mean()
  #print("df7mean")
  #print(df7mean)
  #print(df7.describe())
  #print("Mean="+str(df7.loc[:,'ResponseTime'].mean()))
  #print("Count="+str(df7.count()))
  #print("0.5="+str(df7.quantile()))
  #df8=groupBy(df8,['PurePath'])
  #df78 = pd.merge(df7, df8,  how='left', left_on=['Application','PurePath'], right_on = ['Application','PurePath'])
  dg=datas.groupby(['Hh','Application','PurePath'])
  ddfmean=dict()
  ddfcount=dict()
  for n,g in dg :
    #print(n)
    ddfmean[n]=g.mean()
    ddfcount[n]=g.count()
  for n in ddfmean :
    print(n)
    print(ddfmean[n])
    print(ddfcount[n])
  #df78=pd.merge(dg.get_group(7),dg.get_group[8],  how='outer', on=['Application','PurePath'])
  #OUT.out("merge ",df78 )

#--------------------------------------------------------------------------------------
def filterRows(datas,col,re=' 07:') :
  #filter=(re in datas[col])
  #print("filterRows ")
  filter=( ' 08:' in datas['StartTime'] )
  filter=( datas['StartTime'][11:12] == ' 08' )
  df=datas[ datas['StartTime'].str.contains(' 07') ]
  OUT.out("filterRows ",df)


#-----------------------------------------------------------------------------
#rawDatas=getRawdatas('x.pan')
OUT=OutputHtml()
OUT=OutputTty()
OUT.open()
rawDatas=getRawdatas('PPP.pan')
statsOnKO(rawDatas)
statsOnOK(rawDatas)
#datas=removeAssets(rawDatas)
datas=rawDatas[rawDatas.PurePath.str.contains("assets")==False]
datas['PurePath']=datas['PurePath'].map(coalesceUrl)
#myPlot(datas)

datas['Hh']=datas['StartTime'].map(lambda x: int(x[11:13]) )

#highValues(rawDatas,5000)
#datas=highValues(datas,5000)
#groupBy(datas,['Agent'])
#groupBy(datas,['Hh','PurePath'])
#groupBy(datas,['PurePath','Hh'])
#groupBy(datas,['Application','PurePath'])
#groupBy(datas,['PurePath','Application'])

#filterRows(rawDatas,'StartTime',' 07:')
compareHh(datas)
OUT.close()
