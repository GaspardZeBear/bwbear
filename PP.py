import sys
import logging
from PandasProcessor import *
from Param import *
import click

#--------------------------------------------------------------------------------------
@click.command()
@click.option('--datafile', help='datafile')
@click.option('--formatfile',help='formatfile')
@click.option('--output', default='html')
@click.option('--timegroupby', default='ts1m')
@click.option('--timeformat', default='%H-%M')
@click.option('--decimal', default=',')
@click.option('--highresponsetime', default=5000)
@click.option('--buckets', default='0,100,200,300,400,500,1000,2000,3000,4000,5000,10000,20000,30000,60000,1000000')
@click.option('--autofocusmean', default=100)
@click.option('--autofocuscount', default=30)
@click.option('--ymax', default=0)
@click.option('--ppregex', default='')
@click.option('--timeregex', default='')
@click.option('--ppregexclude', default='')
@click.option('--pandas', default='Pandas')
@click.option('--verbose', is_flag=True, default=False)
@click.option('--quick', is_flag=True, default=False)
@click.option('--nodescribe', is_flag=True, default=False)

def launch(
  datafile,
  formatfile,
  output,
  timegroupby,
  timeformat,
  decimal,
  highresponsetime,
  buckets,
  autofocusmean,
  autofocuscount,
  ymax,
  ppregex,
  timeregex,
  ppregexclude,
  pandas,
  verbose,
  quick,
  nodescribe
  ) :
  p=Param()
  p.set('datafile',datafile)
  p.set('output',output)
  p.set('formatfile',formatfile)
  p.set('pandas',pandas)
  p.set('verbose',verbose)
  p.set('quick',quick)
  p.set('nodescribe',nodescribe)
  p.set('highResponseTime',highresponsetime)
  p.set('buckets',buckets)
  p.set('timeFormat',timeformat)
  p.set('decimal',decimal)
  p.set('ymax',ymax)
  p.set('ppregex',ppregex)
  p.set('timeregex',timeregex)
  p.set('ppregexclude',ppregexclude)
  p.set('timeGroupby',timegroupby)
  p.set('autofocusmean',autofocusmean)
  p.set('autofocuscount',autofocuscount)
  pp=PandasProcessor(p)

#--------------------------------------------------------------------------------------
if __name__ == '__main__':
  #logging.warning("Start")
  launch()
  #logging.warning("End")

