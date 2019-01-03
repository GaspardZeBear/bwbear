import sys
import logging
from PandasProcessor import *
from Param import *
import click

@click.group()
def main():
    pass

#--------------------------------------------------------------------------------------
@main.command()
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
@click.option('--steps', default='')
@click.option('--ppregexclude', default='')
@click.option('--workdir', default='')
@click.option('--verbose', is_flag=True, default=False)
@click.option('--quick', is_flag=True, default=False)
@click.option('--nobuckets', is_flag=True, default=False)
@click.option('--nodescribe', is_flag=True, default=False)
@click.option('--nographs', is_flag=True, default=False)

def ppanalyze(
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
  steps,
  ppregexclude,
  workdir,
  verbose,
  quick,
  nobuckets,
  nodescribe,
  nographs
  ) :
  p=Param()
  p.set('datafile',datafile)
  p.set('output',output)
  p.set('formatfile',formatfile)
  p.set('workdir',workdir)
  p.set('verbose',verbose)
  p.set('nographs',nographs)
  p.set('quick',quick)
  p.set('nodescribe',nodescribe)
  p.set('highResponseTime',highresponsetime)
  p.set('steps',steps)
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
  p.processParam()
  l=p.getAll()
  pp=PandasProcessor(p)
  pp.setBehavior()
  pp.go()
  l=p.getAll()
  l['out'].close()

#--------------------------------------------------------------------------------------
@main.command()
def ppparams() :
  p=Param()
  p.processParam()
  l=p.getAll()
  for pp in sorted(l):
    print(pp + " : " + str(l[pp]))

#--------------------------------------------------------------------------------------
if __name__ == '__main__':
  #logging.warning("Start")
  #ppanalyze()
  main()
  #logging.warning("End")

