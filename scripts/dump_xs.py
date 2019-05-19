#!/usr/bin/env python

import argparse
import sys
import logging
import os
import re
import subprocess
import jinja2

xsecAnalyzer_template = """
inputFiles = [{% for file_name in file_names %}
  "root://cms-xrd-global.cern.ch/{{ file_name }}",{% endfor %}
]

process = cms.Process('XSEC')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic8TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, '{{ global_tag }}', '')
process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32({{ max_events }}),
)

process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.source = cms.Source(
  "PoolSource",
  fileNames          = cms.untracked.vstring(inputFiles),
  duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

process.genxsec = cms.EDAnalyzer("GenXSecAnalyzer")

process.p = cms.Path(process.genxsec)
process.schedule = cms.Schedule(process.p)
"""

def run_cmd(command):
  """Runs given commands and logs stdout and stderr to files
  """
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  stdout = stdout.rstrip('\n')
  stderr = stderr.rstrip('\n')
  return stdout, stderr

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
type_choices = ['data', 'mc']
parser.add_argument('-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
                    help = 'R|Input file containing a list of samples')
parser.add_argument('-o', '--output', dest = 'output', metavar = 'path', required = True, type = str,
                    help = 'R|Output directory where the results will be stored')
parser.add_argument('-f', '--filter', dest = 'filter', metavar = 'pattern', required = False, type = str,
                    default = r'.*',
                    help = 'R|Filter samples by their name')
parser.add_argument('-n', '--max-events', dest = 'max_events', metavar = 'int', required = False, type = int,
                    default = -1,
                    help = 'R|Maximum number of events per file to process')
parser.add_argument('-N', '--max-files', dest = 'max_files', metavar = 'int', required = False, type = int,
                    default = -1,
                    help = 'R|Maximum number of files to process')
parser.add_argument('-g', '--global-tag', dest = 'global_tag', metavar = 'tag', required = False, type = str,
                    default = '94X_mc2017_realistic_v13',
                    help = 'R|Global tag')
parser.add_argument('-F', '--force', dest = 'force', action = 'store_true', default = False,
                    help = "R|Force the creation of output directory if it doesn't exist")
parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
                    help = 'R|Enable verbose printout')
args = parser.parse_args()

logging.basicConfig(
  stream = sys.stdout,
  level  = logging.DEBUG if args.verbose else logging.INFO,
  format = '%(asctime)s - %(levelname)s: %(message)s'
)

if not os.path.isfile(args.input):
  raise ValueError('No such file: %s' % args.input)

sample_name_regex = re.compile(args.filter)

samples = {}
with open(args.input, 'r') as f:
  for line_idx, line in enumerate(f):
    line_stripped = line.rstrip('\n')
    if not line_stripped.startswith('/'):
      continue
    if len(line_stripped.split()) < 5:
      raise RuntimeError('Expected at least 5 columns at line %d in file %s' % (line_idx, args.input))
    line_split = line_stripped.split()
    dbs_key = line_split[0]
    sample_name = line_split[3]
    expected_xs = float(line_split[4])
    if sample_name_regex.match(sample_name):
      logging.debug('Found sample {}'.format(sample_name))
      samples[sample_name] = {
        'dbs_key'     : dbs_key,
        'expected_xs' : expected_xs,
      }

if not os.path.isdir(args.output):
  logging.info('Directory {} does not exist'.format(args.output))
  if not args.force:
    raise ValueError('Use -F/--force to create the output directory %s' % args.output)
  os.makedirs(args.output)

timeleft_cmd = 'voms-proxy-info --timeleft'
timeleft_out, timeleft_err = run_cmd(timeleft_cmd)
if timeleft_err:
  raise RuntimeError("Could not execute '%s' because: %s" % (timeleft_cmd, timeleft_err))
timeleft = int(timeleft_out)
min_hours = 48
if timeleft < min_hours * 3600:
  raise RuntimeError(
    'Proxy must be open at least %d hours; use: voms-proxy-init -voms cms -valid %d:00' % (
      min_hours, min_hours + 1
    )
  )

dasgo_query = "dasgoclient -query='file dataset=%s'"
for sample_name, sample_entry in samples.items():
  dasgo_query_sample = dasgo_query % sample_entry['dbs_key']
  dasgo_out, dasgo_err = run_cmd(dasgo_query_sample)
  if dasgo_err:
    raise RuntimeError("Could not execute '%s' because: %s" % (dasgo_query_sample, dasgo_err))
  sample_files = dasgo_out.split('\n')
  if not sample_files:
    raise RuntimeError('Found no files for sample %s' % sample_name)
  logging.debug('Found {} files for sample {}'.format(len(sample_files), sample_name))
  if args.max_files > 0:
    sample_files = sample_files[0:min(len(sample_files), args.max_files)]
    logging.debug('Limited the nof files to {} in sample {}'.format(len(sample_files), sample_name))
  invalid_paths = list(filter(lambda sample_file: not sample_file.startswith('/store/mc'), sample_files))
  if invalid_paths:
    raise RuntimeError('Found invalid files for sample %s: %s' % (sample_name, ', '.join(invalid_paths)))

  sample_output_dir = os.path.join(args.output, sample_name)
  if not os.path.isdir(sample_output_dir):
    os.makedirs(sample_output_dir)
  cmsrun_logfile = os.path.join(sample_output_dir, 'out.log')
  cmsrun_script = os.path.join(sample_output_dir, 'xsecAnalyzer.py')
  cmsrun_contents = jinja2.Template(xsecAnalyzer_template).render(
    file_names = sample_files,
    global_tag = args.global_tag,
    max_events = args.max_events,
  )
  with open(cmsrun_script, 'w') as f:
    f.write(cmsrun_contents)
  sample_entry['cmd'] = 'cmsRun %s &> %s' % (cmsrun_script, cmsrun_logfile)
  sample_entry['logfile'] = cmsrun_logfile
  logging.info('Wrote file {}'.format(cmsrun_script))

for sample_name, sample_entry in samples.items():
  logging.info('Running cmsRun for {}'.format(sample_name))
  run_cmd(sample_entry['cmd'])
  cmsrun_logfile = sample_entry['logfile']
  if not os.path.isfile(cmsrun_logfile):
    raise RuntimeError('Could not find %s' % cmsrun_logfile)
  xs_actual = -1.
  xs_err_actual = -1.
  xs_units = ''
  with open(cmsrun_logfile, 'r') as f:
    for line in f:
      if line.startswith('After filter: final cross section'):
        line_stripped = line.rstrip('\n')
        line_split = line_stripped.split()
        if len(line_split) != 10:
          logging.error('Unexpected line: %s' % line_stripped)
          continue
        try:
          xs_actual = float(line_split[6])
          xs_err_actual = float(line_split[8])
          xs_units = line_split[9]
        except:
          logging.error('Unable to parse line: %s' % line_stripped)
  if xs_actual > 0. and xs_err_actual > 0.:
    expected_xs = sample_entry['expected_xs']
    logging.warning(
      'Expected xs of {:.6f} pb in sample {}, and measured {:.6f} +/- {:.6f} {}'.format(
        expected_xs, sample_name, xs_actual, xs_err_actual, xs_units
      )
    )
  else:
    logging.error('Unable to parse file %s for cross sections' % cmsrun_logfile)
