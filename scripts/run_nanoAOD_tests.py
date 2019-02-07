#!/usr/bin/env python

import subprocess
import stat
import os
import json
import argparse


def fill_template(params, output_dir, nthreads, nevents, verbose):
  print('Generating cfg file for {} ...'.format(params['name']))
  params['is_mc'] = (params['type'] != 'data')

  if params['is_mc']:
    params['tier'] = 'NANOAODSIM'
  else:
    params['tier'] = 'NANOAOD'

  params['nthreads'] = nthreads
  params['nevents'] = nevents

  base_fn = os.path.join(output_dir, '%s_NANO.{ext}' % params['name'])
  params['fileout'] = base_fn.format(ext = 'root')
  params['py_out'] = base_fn.format(ext = 'py')
  params['log'] = base_fn.format(ext = 'log')

  template = "cmsDriver.py {name} -s NANO --{type} --eventcontent {tier} --datatier {tier} --conditions {cond} " \
             "--nThreads {nthreads} --era {era} --processName=NANO -n {nevents} --fileout {fileout} --python_filename {py_out} " \
             "--filein {file} --no_exec --customise_commands=\"process.MessageLogger.cerr.FwkReport.reportEvery = 1\\n" \
             "from tthAnalysis.NanoAOD.addVariables import addVariables; addVariables(process)\\n" \
             "from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; addJetSubstructureObservables(process)\\n" \
             "from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets; addLeptonSubtractedAK8Jets(process, {is_mc}, '{year}', True)\\n\""
  template_filled = template.format(**params)
  if verbose:
    print(template_filled)

  cmd = subprocess.Popen(template_filled, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
  out, err = cmd.communicate()
  if verbose:
    print(err)
    print(out)
  run_cmd = "echo 'Running {name} ...'\ncmsRun {py_out} &> {log}".format(**params)
  return run_cmd

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)


parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = False, type = str,
  default = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test', 'testCases.json'),
  help = 'R|Input JSON file containing a list of test cases',
)
parser.add_argument(
  '-o', '--output', dest = 'output', metavar = 'directory', required = True, type = str,
  help = 'R|Output directory where the tests will be run',
)
parser.add_argument(
  '-n', '--nevents', dest = 'nevents', metavar = 'int', required = False, type = int, default = 10,
  help = 'R|Number of events per test',
)
parser.add_argument(
  '-t', '--threads', dest = 'threads', metavar = 'int', required = False, type = int, default = 1,
  help = 'R|Number of threads per test',
)
parser.add_argument(
  '-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
  help = 'R|Enable verbose printout',
)
args = parser.parse_args()

input_json = args.input
output_dir = args.output
nevents = args.nevents
nthreads = args.threads
verbose = args.verbose

with open(input_json, 'r') as testCases:
  params_list = json.load(testCases)

if not os.path.isfile(input_json):
  raise ValueError('No such file: %s' % input_json)
if not os.path.isdir(output_dir):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  else:
    raise ValueError('Invalid path: %s' % output_dir)

cmds = []
for params in params_list:
  cmds.append(fill_template(params, output_dir, nthreads, nevents, verbose))

sh_file = os.path.join(output_dir, 'run_all.sh')
with open(sh_file, 'w') as f:
  f.write('#!/bin/bash\n\n')
  f.write('%s\n' % '\n'.join(cmds))

st = os.stat(sh_file)
os.chmod(sh_file, st.st_mode | stat.S_IEXEC)
