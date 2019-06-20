#!/usr/bin/env python

import os
import argparse
import sys
import logging
import subprocess
import hashlib
import urllib

CONFIG = {
  '2016' : {
    'json'   : 'Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt',
    'pileup' : 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/PileUp/pileup_latest.txt',
    'md5sum' : '19d2189b731d6fee4e7ba80b53464206',
  },
  '2017' : {
    'json'   : 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt',
    'pileup' : 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/PileUp/pileup_latest.txt',
    'md5sum' : 'ea3389cd1d992aeaef66b842c5085d05',
  },
  '2018' : {
    'json'   : 'Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt',
    'pileup' : 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/PileUp/pileup_latest.txt',
    'md5sum' : '328bc8dd78121616f440f57ac8f811e2',
  },
}

# Credit to: https://stackoverflow.com/a/3431838/4056193
def md5(fname):
  hash_md5 = hashlib.md5()
  with open(fname, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_md5.update(chunk)
  return hash_md5.hexdigest()

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
parser.add_argument('-s', '--script', dest = 'script', metavar = 'file', required = False, type = str,
                    default = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test', 'pileupCalc.py'),
                    help = 'R|Script file')
parser.add_argument('-e', '--era', dest = 'era', metavar = 'era', required = True, type = str, choices = list(CONFIG.keys()),
                    help = 'R|Era')
parser.add_argument('-o', '--output', dest = 'output', metavar = 'file', required = True, type = str,
                    help = 'R|Output file')
parser.add_argument('-b', '--minbias', dest = 'minbias', metavar = 'xs', required = False, type = int, default = 69200,
                    help = 'R|Minimum bias cross section')
parser.add_argument('-S', '--shift', dest = 'shift', metavar = 'float', required = False, type = float, default = 0.05,
                    help = 'R|Relative up/down shift of minimum bias cross section')
parser.add_argument('-n', '--nbins', dest = 'nbins', metavar = 'int', required = False, type = int, default = 200,
                    help = 'R|Number of bins in pileup histogram')
parser.add_argument('-N', '--name', dest = 'name', metavar = 'histogram', required = False, type = str, default = 'pileup',
                    help = 'R|Default name for the pileup histogram')
parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
                    help = 'R|Enable verbose printout')
args = parser.parse_args()

logging.basicConfig(
  stream = sys.stdout,
  level  = logging.DEBUG if args.verbose else logging.INFO,
  format = '%(asctime)s - %(levelname)s: %(message)s',
)

script_location = args.script
era             = args.era
output          = args.output
minbias_xs      = args.minbias
shift           = args.shift
nbins           = args.nbins
name            = args.name

settings = CONFIG[era]
output_dir = os.path.dirname(output)

if not (0. < shift < 1.):
  raise ValueError("Invalid shift (must be between 0 and 1): %f" % shift)

if not os.path.isfile(script_location):
  raise ValueError("No such scipt: %s" % script_location)

if output_dir and not os.path.isdir(output_dir):
  raise ValueError("Cannot write to %s since it does not exist" % output_dir)

cert_location = os.path.join(
  os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'data', settings['json'],
)
if not os.path.isfile(cert_location):
  raise ValueError('Could not find golden JSON from: %s' % cert_location)

# Download the pileup file
logging.debug('Downloading {}'.format(settings['pileup']))
(filename, headers) = urllib.urlretrieve(settings['pileup'])
logging.debug('Downloaded to: {}'.format(filename))
current_md5 = md5(filename)
if current_md5 != settings['md5sum']:
  raise RuntimeError(
    "Expected md5 '%s' but got '%s' from '%s' -> pileup JSON updated?" % \
    (settings['md5sum'], current_md5, settings['pileup'])
  )

shifts = [('', 0.), ('plus', +shift), ('minus', -shift)]

outputs = []
for shift_pair in shifts:
  histogram_name = name
  if shift_pair[0]:
    histogram_name += '_{}'.format(shift_pair[0])

  output_split = os.path.splitext(output)
  output_shift_name = shift_pair[0] if shift_pair[0] else 'central'
  output_shifted = '{}_{}{}'.format(output_split[0], output_shift_name, output_split[1])

  cmd_args = [
    'python', script_location,
    '-i',               cert_location,
    '--inputLumiJSON',  filename,
    '--calcMode',       'true',
    '--maxPileupBin',   nbins,
    '--numPileupBins',  nbins,
    '--minBiasXsec',    int(minbias_xs * (1. + shift_pair[1])),
    '--pileupHistName', histogram_name,
    output_shifted,
  ]
  cmd_str = map(str, cmd_args)
  logging.debug('Executing: {}'.format(' '.join(cmd_str)))
  cmd = subprocess.Popen(cmd_str)
  out, err = cmd.communicate()
  if err:
    raise RuntimeError(err)
  if not os.path.isfile(output_shifted):
    raise RuntimeError('Unable to produce file: %s' % output_shifted)
  outputs.append(output_shifted)

logging.debug('Hadding outputs to: {}'.format(output))
cmd_args = [ 'hadd', '-f', output ] + outputs
logging.debug('Executing: {}'.format(' '.join(cmd_args)))
cmd = subprocess.Popen(cmd_args)
out, err = cmd.communicate()
if err:
  raise RuntimeError(err)

for output_shifted in outputs:
  logging.debug('Removing: {}'.format(output_shifted))
  os.remove(output_shifted)
