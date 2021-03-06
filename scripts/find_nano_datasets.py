#!/usr/bin/env python

from FWCore.PythonUtilities.LumiList import LumiList

import argparse
import logging
import sys
import os
import re
import subprocess
import datetime
import ast
import psutil
import signal
import shlex
import collections

logging.basicConfig(
  stream = sys.stdout,
  level  = logging.INFO,
  format = '%(asctime)s - %(levelname)s: %(message)s'
)

GOLDEN_JSONS = {
  '2016' : 'Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt',
  '2017' : 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt',
  '2018' : 'Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt',
}

# see https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2018AnalysisMissingMiniAODPrompt
MINIAOD_RUNLUMI_EXCEPTIONS = [
  '/EGamma/Run2018D-PromptReco-v2/MINIAOD', # 171 files corrupted
  '/SingleMuon/Run2018D-PromptReco-v2/MINIAOD', # 73 files corrupted
  '/Tau/Run2018D-PromptReco-v2/MINIAOD', # 11 files corrupted
]

def load_golden_jsons(golden_json_path):
  if not os.path.isfile(golden_json_path):
    raise RuntimeError("No such file: %s" % golden_json_path)
  lumi_obj = LumiList(golden_json_path)
  lumis = lumi_obj.getLumis()
  runlumi_dict = {}
  for run, lumi in lumis:
    if run not in runlumi_dict:
      runlumi_dict[run] = []
    assert(lumi not in runlumi_dict[run])
    runlumi_dict[run].append(lumi)
  return runlumi_dict

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

class Alarm(Exception):
  pass

def alarm_handler(signum, frame):
  raise Alarm

class Command(object):
  def __init__(self, cmd):
    self.cmd = cmd
    self.process = None
    self.out = None
    self.err = None
    self.success = False

  def run(self, max_tries = 20, timeout = 5):
    ntries = 0
    while not self.success:
      if ntries > max_tries:
        break
      ntries += 1
      signal.signal(signal.SIGALRM, alarm_handler)
      signal.alarm(timeout)
      self.process = subprocess.Popen(shlex.split(self.cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
      try:
        self.out, self.err = self.process.communicate()
        signal.alarm(0)
      except Alarm:
        parent = psutil.Process(self.process.pid)
        for child in parent.children(recursive = True):
          child.kill()
        parent.kill()
      else:
        self.success = True

def get_docstring():
  execution_datetime = '{date:%Y-%m-%d %H:%M:%S}'.format(date = datetime.datetime.now())
  execution_command = ' '.join([os.path.basename(__file__)] + sys.argv[1:])
  docstring = "# file generated at {} with the following command:\n# {}\n".format(execution_datetime, execution_command)
  return docstring

def parse_input(fn):
  lines = []
  with open(fn, 'r') as f:
    for line in f:
      line_stripped = line.rstrip('\n')
      line_split = line_stripped.split()
      line_to_add = [ line_stripped ]
      if line_split:
        line_1st_col = line_split[0]
        if line_1st_col.endswith(('/MINIAODSIM', '/MINIAOD')):
          line_to_add.append(line_1st_col)
      lines.append(line_to_add)
    logging.info('Found {} dataset(s) in file {}'.format(len(list(filter(lambda line: len(line) > 1, lines))), fn))
    return lines

def run_query(query_str, return_err = False):
  cmd = Command(query_str)
  cmd.run()
  if return_err:
    return cmd.out.rstrip('\n'), cmd.err.rstrip('\n')
  else:
    return cmd.out.rstrip('\n')

def check_proxy():
  proxy_query = 'voms-proxy-info -timeleft'
  proxy_out = run_query(proxy_query)
  if not proxy_out:
    logging.error('Got no output from command: {}'.format(proxy_query))
    return False
  try:
    timeleft = int(proxy_out)
  except:
    logging.error('Unable to parse commdn: {}: {}'.format(proxy_query, proxy_out))
    return False
  if timeleft < 3600:
    logging.error('Proxy remains open for {} seconds, but should be open for at least an hour'.format(timeleft))
    logging.error('Run: voms-proxy-init -voms cms -valid 2:00')
    return False
  else:
    return True

def get_nanoaod(id_str, is_data):
  if not id_str:
    raise ValueError("Cannot use empty ID string")
  query_str = "dasgoclient -query='dataset dataset=/*/*{}*/NANOAOD{} status=* | " \
              "grep dataset.name | grep dataset.dataset_access_type'".format(id_str, '' if is_data else 'SIM')
  query_out = run_query(query_str)
  if not query_out:
    raise RuntimeError("No output returned by command: %s" % query_str)
  result = {}
  nof_invalid = 0
  for line in query_out.split('\n'):
    line_split = line.split()
    if not line_split:
      continue
    dbs_name = line_split[0]
    dbs_status = line_split[1]
    if dbs_status == 'INVALID':
      nof_invalid += 1
      continue
    assert(dbs_name not in result)
    result[dbs_name] = dbs_status
  logging.info(
    'Found {} {} dataset(s), plus {} invalid dataset(s)'.format(len(result), 'data' if is_data else 'MC', nof_invalid)
  )
  return result

def read_nanoaod(fn):
  result = {}
  nof_invalid = 0
  assert(os.path.isfile(fn))
  with open(fn, 'r') as f:
    for line in f:
      line_split = line.rstrip('\n').split()
      assert(len(line_split) == 2)
      dbs_name = line_split[0]
      dbs_status = line_split[1]
      assert(dbs_status in [ 'VALID', 'PRODUCTION', 'INVALID' ])
      if dbs_status == 'INVALID':
        nof_invalid += 1
        continue
      assert(dbs_name not in result)
      result[dbs_name] = dbs_status
  logging.info(
    'Found {} dataset(s) plus {} invalid dataset(s) in file {}'.format(len(result), nof_invalid, fn)
  )
  return result

def merge_dicts(dict_first, dict_second):
  assert(not (set(dict_first.keys()) & set(dict_second.keys())))
  dict_result = dict_first.copy()
  dict_result.update(dict_second)
  return dict_result

def resolve_candidate(nanoaod_cands):
  if not nanoaod_cands:
    return ''
  nanoaod_parents = {}
  for nanoaod in nanoaod_cands:
    query_str = "dasgoclient -query='parent dataset={}'".format(nanoaod)
    query_out = run_query(query_str)
    if not query_out:
      raise RuntimeError("Unable to find parent for: %s" % nanoaod)
    query_out_split = query_out.split('\n')
    if len(query_out_split) != 1:
      raise RuntimeError("Got unexpected result from query %s: %s" % (query_str, query_out))
    nanoaod_parent = query_out_split[0]
    if not nanoaod_parent.endswith(('MINIAOD', 'MINIAODSIM')):
      raise RuntimeError("Not a valid parent to %s: %s" % (nanoaod, nanoaod_parent))
    assert(nanoaod_parent not in nanoaod_parents)
    nanoaod_parents[nanoaod_parent] = nanoaod
  return nanoaod_parents

def get_size(dbs_name):
  query_str = "dasgoclient -query='dataset dataset={} | grep dataset.nevents'".format(dbs_name)
  query_out = run_query(query_str)
  nevents_str = list(filter(lambda line: not line.startswith('['), query_out.split('\n')))
  if len(nevents_str) != 1:
    raise RuntimeError("Got invalid output from command %s: %s" % (query_str, query_out))
  return int(nevents_str[0])

def get_runlumi(dbs_name):
  query_str = "dasgoclient -query='run,lumi dataset={}'".format(dbs_name)
  query_out = run_query(query_str)
  runlumis = {}
  for line in query_out.split('\n'):
    line_split = line.split()
    if len(line_split) != 2:
      raise RuntimeError("Unexpected line from command %s: %s" % (query_str, line))
    run = int(line_split[0])
    lumis = set(ast.literal_eval(line_split[1]))
    assert(run not in runlumis)
    runlumis[run] = lumis
  return runlumis

def convert_to_ranges(lumilist):
  lumilist = sorted(set(lumilist))
  lumi_min = min(lumilist)
  lumi_max = max(lumilist)
  if lumi_max in [ lumi_min, lumi_min + 1 ]:
    return [ [ lumi_min, lumi_max ] ]
  lumi_ranges = []
  lumi_first = lumi_min
  lumi_last = lumi_min
  for lumi in lumilist[1:]:
    if lumi != (lumi_last + 1) or lumi == lumi_max:
      lumi_ranges.append([ lumi_first, lumi_last ])
      lumi_first = lumi
    lumi_last = lumi
  return str(lumi_ranges).replace(' ', '')

def runlumi_match(miniaod, nanoaod, nanoaod_status, golden_json):
  if miniaod.endswith('SIM'):
    assert(nanoaod.endswith('SIM'))
    return True
  else:
    assert(not nanoaod.endswith('SIM'))
  if nanoaod_status == 'PRODUCTION':
    logging.warning("Dataset {} is in production".format(nanoaod))
    return True

  miniaod_size = get_size(miniaod)
  nanoaod_size = get_size(nanoaod)
  if nanoaod_size > miniaod_size:
    RuntimeError(
      "Dataset %s has more events (%d) than dataset %s (%s)" % \
      (nanoaod, nanoaod_size, miniaod, miniaod_size)
    )
  elif nanoaod_size < miniaod_size:
    logging.error(
      "The number of events in dataset {} ({}) does not match to the number of events in dataset {} ({})".format(
        miniaod, miniaod_size, nanoaod, nanoaod_size
      )
    )
    retval = True

    runlumi_miniaod = get_runlumi(miniaod)
    runlumi_nanoaod = get_runlumi(nanoaod)
    run_missing_miniaod = set(runlumi_nanoaod.keys()) - set(runlumi_miniaod.keys())
    if run_missing_miniaod:
      raise RuntimeError(
        "Found %d run numbers that are present in %s but not in %s: %s" % \
        (len(run_missing_miniaod), nanoaod, miniaod, ', '.join(map(str, list(run_missing_miniaod))))
      )
    run_missing_nanoaod = sorted(list(set(runlumi_miniaod.keys()) - set(runlumi_nanoaod.keys())))
    if run_missing_nanoaod:
      logging.error(
        "Found {} run numbers that are present in {} but not in {}: {}".format(
          len(run_missing_nanoaod), miniaod, nanoaod, ', '.join(map(str, run_missing_nanoaod))
        )
      )
    run_missing_nanoaod_golden = [ run for run in run_missing_nanoaod if run in golden_json ]
    run_missing_nanoaod_not_golden = [ run for run in run_missing_nanoaod if run not in golden_json ]
    if run_missing_nanoaod_golden:
      logging.error(
        "The following in golden JSON but not in {}: {}".format(
          nanoaod, ', '.join(map(str, run_missing_nanoaod_golden))
        )
      )
      retval = False
    if run_missing_nanoaod_not_golden:
      logging.info(
        "The following runs missing in {} not golden: {}".format(
          nanoaod, ', '.join(map(str, run_missing_nanoaod_not_golden))
        )
      )
    for run in runlumi_miniaod:
      if run not in golden_json:
        continue
      if run not in runlumi_nanoaod:
        continue
      lumis_miniaod = runlumi_miniaod[run]
      lumis_nanoaod = runlumi_nanoaod[run]
      lumis_missing_miniaod = sorted(list(lumis_nanoaod - lumis_miniaod))
      if lumis_missing_miniaod:
        raise RuntimeError(
          "Found lumis at run %d that are present in %s but not in %s: %s" % \
          (run, nanoaod, miniaod, convert_to_ranges(lumis_missing_miniaod))
        )
      lumis_missing_nanoaod = sorted(list(lumis_miniaod - lumis_nanoaod))
      if lumis_missing_nanoaod:
        logging.error(
          "Found lumis at run {} that are present in {} but not in {}: {}".format(
            run, miniaod, nanoaod, convert_to_ranges(lumis_missing_nanoaod)
          )
        )
      lumis_missing_nanoaod_golden = [ lumi for lumi in lumis_missing_nanoaod if lumi in golden_json[run] ]
      lumis_missing_nanoaod_not_golden = [ lumi for lumi in lumis_missing_nanoaod if lumi not in golden_json[run] ]
      if lumis_missing_nanoaod_golden:
        logging.error(
          "The following lumis at run {} in golden JSON but not in {}: {}".format(
            run, nanoaod, convert_to_ranges(lumis_missing_nanoaod_golden)
          )
        )
        retval = False
      if lumis_missing_nanoaod_not_golden:
        logging.error(
          "The following lumis at run {} missing in {} not golden: {}".format(
            run, nanoaod, convert_to_ranges(lumis_missing_nanoaod_not_golden)
          )
        )
    if not retval and miniaod in MINIAOD_RUNLUMI_EXCEPTIONS:
      logging.info(
        "Dataset {} has corrupted files, which is the reason why {} is missing events".format(miniaod, nanoaod)
      )
      retval = True
    return retval
  else:
    logging.info("Number of events in {} match to the number of events in {}: {}".format(miniaod, nanoaod, miniaod_size))
  return True

def find_matching_nano(miniaods, dbs_nano, data_str, mc_str):
  result = {}
  for miniaod in miniaods:
    miniaod_split = miniaod.split('/')
    assert(len(miniaod_split) == 4)
    miniaod_lead = miniaod_split[1]
    miniaod_sublead = miniaod_split[2]
    miniaod_tier = miniaod_split[3]
    if miniaod_tier == 'MINIAOD':
      assert(miniaod_sublead.startswith('Run201'))
      miniaod_sublead_split = miniaod_sublead.split('-')
      assert(len(miniaod_sublead_split) > 1)
      nanoaod_sublead = '{}.*-{}'.format(miniaod_sublead_split[0], data_str)
    elif miniaod_tier == 'MINIAODSIM':
      assert(miniaod_sublead.startswith('RunII'))
      miniaod_sublead_split = miniaod_sublead.split('-')
      assert (len(miniaod_sublead_split) > 1)
      nanoaod_sublead = re.sub('MiniAOD(v\d)?', mc_str, miniaod_sublead_split[0])
    else:
      raise RuntimeError('Unexpected tier %s found in DBS name %s' % (miniaod_tier, miniaod))
    nanoaod_re_str = '/{}/{}.*/{}'.format(miniaod_lead, nanoaod_sublead, miniaod_tier.replace('MINI', 'NANO'))
    nanoaod_re = re.compile(nanoaod_re_str)
    nanoaod_cands = []
    for nanoaod in dbs_nano:
      if nanoaod_re.match(nanoaod):
        nanoaod_cands.append(nanoaod)
    nanoaod_parents = resolve_candidate(nanoaod_cands)
    if miniaod not in nanoaod_parents:
      logging.error('No candidates found for: {}'.format(miniaod))
    else:
      logging.debug('Found candidate for {}: {}'.format(miniaod, nanoaod_parents[miniaod]))
    result[miniaod] = nanoaod_parents
  return result

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str, nargs = '+',
  help = 'R|Input text file(s) containing list of MINIAOD(SIM) files',
)
parser.add_argument(
  '-j', '--input-mc', dest = 'input_mc', metavar = 'file', required = False, type = str, default = '',
  help = 'R|Input file containing list of all NANOAODSIM files',
)
parser.add_argument(
  '-k', '--input-data', dest = 'input_data', metavar = 'file', required = False, type = str, default = '',
  help = 'R|Input file containing list of all NANOAOD files',
)
parser.add_argument(
  '-p', '--prefix', dest = 'prefix', metavar = 'str', required = False, type = str, default = 'nano',
  help = 'R|Prefix added to the input file names',
)
parser.add_argument(
  '-d', '--data', dest = 'data', metavar = 'str', required = False, type = str, default = 'Nano25Oct2019',
  help = 'R|Identifier in DBS names of data NanoAOD',
)
parser.add_argument(
  '-m', '--mc', dest = 'mc', metavar = 'str', required = False, type = str, default = 'NanoAODv6',
  help = 'R|Identifier in DBS names of MC NanoAOD',
)
parser.add_argument(
  '-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
  help = 'R|Enable verbose printout',
)
args = parser.parse_args()

docstring = get_docstring()

if args.verbose:
  logging.getLogger().setLevel(logging.DEBUG)

if not args.prefix:
  raise ValueError("Cannot use empty prefix in the output file names")

data = collections.OrderedDict()
for input_file in args.input:
  if not os.path.isfile(input_file):
    raise ValueError("No such file: %s" % input_file)
  data[os.path.abspath(input_file)] = parse_input(input_file)

if not check_proxy():
  sys.exit(1)

dbs_data = read_nanoaod(args.input_data) if args.input_data else get_nanoaod(args.data, True)
dbs_mc = read_nanoaod(args.input_mc) if args.input_mc else get_nanoaod(args.mc, False)
dbs_nano = merge_dicts(dbs_data, dbs_mc)
logging.info('Considering {} dataset(s) in total'.format(len(dbs_nano)))

json_base_path = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'data')
golden_jsons = {}
for era in GOLDEN_JSONS:
  golden_jsons['Run{}'.format(era)] = load_golden_jsons(os.path.join(json_base_path, GOLDEN_JSONS[era]))

for input_file in data:
  miniaods = list(map(lambda line_out: line_out[1], filter(lambda line_in: len(line_in) > 1, data[input_file])))
  nanoaod_parents = find_matching_nano(miniaods, dbs_nano, args.data, args.mc)
  nanoaods = { miniaod : (nanoaod_parents[miniaod][miniaod] if miniaod in nanoaod_parents[miniaod] else '') for miniaod in miniaods }
  max_width_nanoaod = max(map(len, nanoaods.values())) + 1
  output_fn_base = '{}_{}'.format(args.prefix, os.path.basename(input_file))
  output_fn = os.path.join(os.path.dirname(input_file), output_fn_base)
  with open(output_fn, 'w') as f:
    unmatched_miniaods = []
    for line in data[input_file]:
      if len(line) == 1:
        f.write('{}\n'.format(line[0]))
      elif len(line) == 2:
        miniaod = line[1]
        nanoaod_cand = nanoaods[miniaod]
        if nanoaod_cand and not nanoaod_cand.endswith('SIM'):
          golden_json_eras = [ era for era in golden_jsons if era in nanoaod_cand ]
          if len(golden_json_eras) != 1:
            raise RuntimeError("Unable to find golden JSON for %s" % nanoaod_cand)
          golden_json_era = golden_json_eras[0]
          logging.info("Golden JSON era for dataset {}: {}".format(nanoaod_cand, golden_json_era))
          golden_json = golden_jsons[golden_json_era]
        else:
          golden_json = {}
        if nanoaod_cand and runlumi_match(miniaod, nanoaod_cand, dbs_nano[nanoaod_cand], golden_json):
          line_remaining = line[0].replace(miniaod, '').lstrip()
          f.write('{}{}\n'.format(nanoaod_cand.ljust(max_width_nanoaod), line_remaining))
        else:
          unmatched_miniaods.append(line[1])
      else:
        assert(False)
    if unmatched_miniaods:
      f.write('\n# Unable to find matching NANOAOD datasets for the following MINIAOD datasets:\n')
      for miniaod in unmatched_miniaods:
        f.write('# {}\n'.format(miniaod))
        if nanoaod_parents[miniaod]:
          for miniaod_cand, nanoaod_cand in nanoaod_parents[miniaod].items():
            f.write('#   {} -> {}\n'.format(miniaod_cand, nanoaod_cand))
    f.write('\n{}\n'.format(docstring))
  logging.info('Wrote file: {}'.format(output_fn))
