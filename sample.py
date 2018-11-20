import pandas as pd
datas=[
       [7,'fast.com','login.htm',10,0],
       [7,'fast.com','do.htm',15,0],
       [7,'fast.com','logout.htm',19,0],
       [7,'normal.fr','login.htm',20,1],
       [7,'normal.fr','do.htm',25,1],
       [7,'normal.fr','logout.htm',29,1],
       [7,'slow.com','login.htm',30,2],
       [7,'slow.com','do.htm',35,2],
       [7,'slow.com','logout.htm',39,2],
       [8,'fast.com','login.htm',11,0],
       [8,'fast.com','do.htm',15,0],
       [8,'fast.com','logout.htm',19,0],
       [8,'normal.fr','login.htm',21,1],
       [8,'normal.fr','do.htm',26,1],
       [8,'normal.fr','logout.htm',29,1],
       [8,'slow.com','login.htm',31,2],
       [8,'slow.com','do.htm',36,2],
       [8,'slow.com','logout.htm',39,2],
       [9,'fast.com','login.htm',11,0],
       [9,'fast.com','do.htm',16,0],
       [9,'fast.com','logout.htm',19,0],
       [9,'normal.fr','login.htm',22,1],
       [9,'normal.fr','do.htm',27,1],
       [9,'normal.fr','logout.htm',29,1],
       [9,'slow.com','login.htm',33,2],
       [9,'slow.com','do.htm',37,2],
       [9,'slow.com','logout.htm',39,2],
      ]
df=pd.DataFrame(datas,columns=['hh','domain','url','time','val2'])
print(df)
#dg=df.groupby(['hh','domain'])['time']
#print(dg)
#print(dg.describe())
#print(dg.groups)
#for u,g in dg :
#  print(u)
#  print(g.mean())
#pi=pd.pivot_table(df,index=['hh','domain'],values='time')
#print(pi)

df7=df[ (df['hh'] == 7) ]
print(df7)
df8=df[ (df['hh'] == 8) ]
print(df8)
df9=df[ (df['hh'] == 8) ]
print(df9)
df78=pd.merge(df7, df8,  how='outer', on=['domain','url'])
df78['deltaA']=df78['time_y'] - df78['time_x']
df78['deltaP']=(df78['time_y'] - df78['time_x'])/df78['time_x']
#print(df78)
print(pd.merge(df[ (df['hh'] == 7) ],df[ (df['hh'] == 8) ],  how='outer', on=['domain','url']))
