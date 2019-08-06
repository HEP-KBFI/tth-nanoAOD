#!/usr/bin/env python

import argparse
import os
import re

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

MAX_LUMIS = 100000
MAX_FILE_RE = re.compile("Largest file .+ contains (?P<max_file_events>\d+) events")
LUMI_ERROR_RE = re.compile("ERROR: found \d+ > {} lumis in block .+".format(MAX_LUMIS))
DSET_ERRORS_RE = re.compile("Dataset (?P<dset>.+) is NOT compatible with EventAwareLumiBased splitting .+")
DSET_PASS_RE = re.compile("Dataset (?P<dset>.+) is compatible with EventAwareLumiBased splitting .+")

def parser_errors(infn, outfn = ''):
  if not os.path.isfile(infn):
    raise ValueError("No such file: %s" % infn)

  erroneous_datasets = {}
  with open(infn, 'r') as infile:
    current_dataset = ''
    nof_events = -1
    nof_errors = 0

    for line in infile:
      line_stripped = line.rstrip('\n')
      if not line:
        continue

      max_file_match = MAX_FILE_RE.match(line_stripped)
      dset_error_match = DSET_ERRORS_RE.match(line_stripped)
      dset_pass_match = DSET_PASS_RE.match(line_stripped)

      if line_stripped.startswith('Checking'):
        current_dataset = line_stripped.split()[1]
        nof_events = -1
        nof_errors = 0
      elif max_file_match:
        assert(current_dataset)
        nof_events = int(max_file_match.group('max_file_events'))
      elif LUMI_ERROR_RE.match(line_stripped):
        assert(current_dataset)
        nof_errors += 1
      elif dset_error_match:
        assert(dset_error_match.group('dset') == current_dataset)
        assert(nof_errors > 0)
        assert(nof_events > 0)
        assert(current_dataset not in erroneous_datasets)
        erroneous_datasets[current_dataset] = nof_events
        current_dataset = ''
        nof_events = -1
        nof_errors = 0
      elif dset_pass_match:
        assert(dset_pass_match.group('dset') == current_dataset)
        current_dataset = ''
        nof_events = -1
        nof_errors = 0

  out = '\n'.join(map(lambda entry: '{} {}'.format(*entry), erroneous_datasets.items()))
  if out:
    if outfn:
      outdir = os.path.dirname(outfn)
      if not os.path.isdir(outdir):
        os.makedirs(outdir)
      with open(outfn, 'w') as outfile:
        outfile.write('{}\n'.format(out))
    else:
      print(out)
  else:
    print('No datasets having a file block containing more than 100000 lumis were found')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  parser.add_argument(
    '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
    help = 'R|Input log file of count_lumis_datasets.sh',
  )
  parser.add_argument(
    '-o', '--output', dest = 'output', metavar = 'file', required = False, type = str, default = '',
    help = 'R|Output file name',
  )
  args = parser.parse_args()

  parser_errors(args.input, args.output)
