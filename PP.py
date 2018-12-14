import sys
import logging
from PandasProcessor import *
from Param import *
import click

#--------------------------------------------------------------------------------------
@click.command()
@click.option('--datafile', help='datafile')
@click.option('--formatfile', prompt='formatfile')
@click.option('--output', default='html', type=click.Choice(['html', 'tty']))
@click.option('--timeGroupby', default='ts1m')
@click.option('--timeFormat', default='%H-%M')
@click.option('--highResponseTime', default=5000)
#@click.option('--pandas', prompt='pandas')
@click.option('--verbose', is_flag=True, default=False)

def launch() :
  p=Param()
  p.set('datafile',datafile)
  p.set('output',output)
  p.set('formatfile',formatfile)
  p.set('pandas',pandas)
  p.set('verbose',verbose)
  p.set('highResponseTime',highResponseTime)
  p.set('timeFormat',timeFormat)
  p.set('timeGroupby',timeGroupby)
  pp=PandasProcessor(p)

#--------------------------------------------------------------------------------------
if __name__ == '__main__':
  launch()

