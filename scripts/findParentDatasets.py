#!/usr/bin/env python

import argparse
import logging
import subprocess
import time
import sys
import os
import re

logging.basicConfig(
  stream = sys.stdout,
  level  = logging.INFO,
  format = '%(asctime)s - %(levelname)s: %(message)s'
)

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def run_cmd(cmd_str):
  cmd = subprocess.Popen(cmd_str, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
  stdout, stderr = cmd.communicate()
  if stderr:
    raise RuntimeError("Caught an error while executing '%s': %s" % (cmd_str, stderr))
  return stdout.rstrip('\n')

def get_dataset_info(dataset, info):
  return run_cmd(
    "dasgoclient -query='dataset={dataset} | grep dataset.{key}' -unique | grep -v '^\\['".format(
      dataset = dataset,
      key     = info,
    )
  )

def get_date(dataset):
  date_str = get_dataset_info(dataset, 'last_modification_date')
  try:
    date_int = int(date_str)
  except ValueError:
    logging.warning("Could not get proper date for {dataset}, got '{response}' instead".format(
      dataset  = dataset,
      response = date_str,
    ))
    date_int = 0
  return date_int

def get_nevents(dataset):
  nevent_str = get_dataset_info(dataset, 'nevents')
  try:
    nevent_int = int(nevent_str)
  except ValueError:
    logging.warning("Could not get proper event count for {dataset}, got '{response}' instead".format(
      dataset  = dataset,
      response = nevent_str,
    ))
    nevent_int = -1
  return nevent_int

def get_parent(dataset):
  return run_cmd("dasgoclient -query='parent dataset={dataset}'".format(dataset = dataset))

def miniaod_str(miniaod_cands, add_comment = True):
  miniaod_latest_count = 0
  miniaod_largest_count = 0
  miniaod_latest = ''
  miniaod_largest = ''
  for miniaod_cand in miniaod_cands:
    if miniaod_cand['date'] > miniaod_latest_count:
      miniaod_latest_count = miniaod_cand['date']
      miniaod_latest = miniaod_cand['name']
    if miniaod_cand['nevent'] > miniaod_largest_count:
      miniaod_largest_count = miniaod_cand['nevent']
      miniaod_largest = miniaod_cand['name']

  if miniaod_latest == miniaod_largest:
    for miniaod_cand in miniaod_cands:
      if miniaod_cand['name'] == miniaod_latest:
        miniaod_cand['comment'] = 'LARGEST and NEWEST'
  else:
    for miniaod_cand in miniaod_cands:
      if miniaod_cand['name'] == miniaod_latest:
        miniaod_cand['comment'] = 'NEWEST'
      elif miniaod_cand['name'] == miniaod_largest:
        miniaod_cand['comment'] = 'LARGEST'

  miniaod_cand_strs = []
  for miniaod_cand in miniaod_cands:
    miniaod_cand_str = '\t{} ({} events, last modified at {}'.format(
      miniaod_cand['name'], miniaod_cand['nevent'], miniaod_cand['date_str']
    )
    if miniaod_cand['comment'] and add_comment:
      miniaod_cand_str += ', {}'.format(miniaod_cand['comment'])
    miniaod_cand_str += ')'
    miniaod_cand_strs.append(miniaod_cand_str)
  return ',\n'.join(miniaod_cand_strs)

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)

parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
  help = 'R|Input text file containing list of MINIAODSIM files',
)
parser.add_argument(
  '-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
  help = 'R|Enable verbose printout',
)
args = parser.parse_args()

if args.verbose:
  logging.getLogger().setLevel(logging.DEBUG)

input_fn = args.input
if not os.path.isfile(input_fn):
  raise ValueError("No such file: %s" % input_fn)

time_left_str = run_cmd('voms-proxy-info --actimeleft')
try:
  time_left = int(time_left_str)
except ValueError as err:
  raise RuntimeError("Could not convert the time until VOMS proxy closes (%s) to string")
if int(time_left / 3600) == 0:
  raise RuntimeError("The proxy must be open at least one hour!")

miniaod_re = re.compile(r'^\/.*\/.*\/MINIAODSIM$')

input_miniaods = []
with open(input_fn, 'read') as input_f:
  for line in input_f:
    # first column, require to be matched to MINIAODSIM regex
    line_split = line.rstrip('\n').split()
    if not line_split:
      # empty line
      continue
    miniaod_cand = line_split[0]
    if not miniaod_re.match(miniaod_cand):
      # does not match to the regex
      continue
    input_miniaods.append(miniaod_cand)

logging.info("Found {} datasets".format(len(input_miniaods)))

aod_parents = {}
gensim_parents = {}

aod_missing = []
gensim_missing = []

for miniaod_cand in input_miniaods:
  logging.debug("Fetching information about {dataset} ...".format(dataset = miniaod_cand))
  miniaod_date = get_date(miniaod_cand)
  miniaod_nevents = get_nevents(miniaod_cand)
  miniaod_entry = {
    'name'     : miniaod_cand,
    'nevent'   : miniaod_nevents,
    'date'     : miniaod_date,
    'date_str' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(miniaod_date)),
    'comment'  : '',
  }

  aod_parent = get_parent(miniaod_cand)
  if not aod_parent:
    logging.warning("Could not find AOD parent for {miniaod}".format(miniaod = miniaod_cand))
    aod_missing.append(miniaod_entry)
    continue
  if aod_parent not in aod_parents:
    aod_parents[aod_parent] = []
  aod_parents[aod_parent].append(miniaod_entry)

  gensim_parent = get_parent(aod_parent)
  if not gensim_parent:
    logging.warning(
      "Could not find GENSIM parent for {aod} (which is a parent of {miniaod})".format(
        aod     = aod_parent,
        miniaod = miniaod_cand,
      )
    )
    gensim_missing.append(miniaod_entry)
    continue
  if gensim_parent not in gensim_parents:
    gensim_parents[gensim_parent] = []
  gensim_parents[gensim_parent].append(miniaod_entry)

for aod_parent, miniaod_cands in aod_parents.items():
  if len(miniaod_cands) > 1:
    logging.warning(
      "Multiple MINIAODSIM files coming from the same file {aod}:\n{miniaods}".format(
        aod      = aod_parent,
        miniaods = miniaod_str(miniaod_cands),
      )
    )
for gensim_parent, miniaod_cands in gensim_parents.items():
  if len(miniaod_cands) > 1:
    logging.warning(
      "Multiple MINIAODSIM files coming from the same file {gensim}:\n{miniaods}".format(
        gensim   = gensim_parent,
        miniaods = miniaod_str(miniaod_cands),
      )
    )
if aod_missing:
  logging.warning("Could not find AODSIM for:\n{miniaods}".format(miniaods = miniaod_str(aod_missing, False)))

if gensim_missing:
  logging.warning("Could not find GENSIM for:\n{miniaods}".format(miniaods = miniaod_str(gensim_missing, False)))
