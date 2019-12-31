#!/usr/bin/env python

import jinja2
import re
import argparse
import os.path

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

HLT_SUFFIX = re.compile('.*_v\d+$')
HLT_DICT = """
          {
            'name'        : '{{hlt_path}}',
            'int_lumi'    : {{int_lumi}},
            'unprescaled' : {{unprescaled}},
            'runs'        : [{% for run in runs %}
              {{run[0]}}, # {{run[1]}}, {{run[2]}}/pb
            {%- endfor %}
            ],
          },
"""
HLT_VSTRING = """
        run_ranges = cms.vstring({% for run in runs %}
          '{{run[0][0]}}-{{run[0][1]}}', # {{run[1]}}, {{run[2]}}/pb
        {%- endfor %}
        ),
"""
INT_LUMIS = {
  2016 : 35.9,
  2017 : 41.5,
  2018 : 59.7,
}
RUN_RANGES = {
  2016 : [ 273150, 284044 ],
  2017 : [ 297047, 306462 ],
  2018 : [ 315257, 325175 ],
}

def read_results(input_file_name):
  assert(os.path.isfile(input_file_name))
  results = []
  with open(input_file_name, 'r') as input_file:
    for line in input_file:
      if line.startswith('#'):
        continue
      line_stripped = line.rstrip()
      if not line_stripped:
        continue
      line_split = line_stripped.split(',')
      assert(len(line_split) == 6)
      run_fill = line_split[0].split(':')
      run = int(run_fill[0])
      name = line_split[3]
      title = name
      if HLT_SUFFIX.match(title):
        title = '_'.join(title.split('_')[:-1])
      recorded = float(line_split[5])
      results.append({
        'title'     : title,
        'name'      : name,
        'run'       : run,
        'recorded'  : recorded,
      })
  return results

def get_run_ranges(runs):
  run_ranges = []
  last_run = -1
  run_count = 0
  for run_idx, run in enumerate(runs):
    if (last_run + 1) != run and run_idx > 0:
      run_ranges.append([last_run - run_count, last_run])
      last_run = run
      run_count = 0
    else:
      last_run = run
      if run_idx > 0:
        run_count += 1
  if last_run == runs[-1]:
    run_ranges.append([ last_run - run_count, last_run ])

  run_ranges_expanded = []
  for run_range in run_ranges:
    run_ranges_expanded.extend(list(range(run_range[0], run_range[1] + 1)))
  assert(run_ranges_expanded == runs)
  return run_ranges

def get_era(runs):
  min_run = min(runs)
  max_run = max(runs)
  for era in RUN_RANGES:
    min_run_exp = RUN_RANGES[era][0]
    max_run_exp = RUN_RANGES[era][1]
    if min_run >= min_run_exp and max_run <= max_run_exp:
      return era
  raise RuntimeError("Unable to determine the era for the run ranges!")

def get_run_assoc(results, run_ranges):
  run_assoc = []
  for run_range in run_ranges:
    names = []
    recorded = 0.
    for run in range(run_range[0], run_range[1] + 1):
      run_stats = [ (result['name'], result['recorded']) for result in results if result['run'] == run ]
      assert(len(run_stats) == 1)
      run_stats = run_stats[0]
      if run_stats[0] not in names:
        names.append(run_stats[0])
      recorded += run_stats[1]
    run_assoc.append(( run_range, '/'.join(names), round(recorded, 3) ))
  return run_assoc

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  parser.add_argument('-i', '--input', dest = 'input', metavar = 'file', required = True, type = str, default = '',
    help = 'R|Output of brilcalc'
  )
  parser.add_argument(
    '-v', '--vstring', dest = 'vstring', action = 'store_true', default = False,
    help = 'R|Fill vstring template',
  )
  args = parser.parse_args()
  results = read_results(args.input)

  if results:
    assert(all(results[0]['title'] == result['title'] for result in results[1:]))
  recorded_sum = sum(result['recorded'] for result in results) / 1000.
  runs = sorted(result['run'] for result in results)
  run_ranges = get_run_ranges(runs)
  era = get_era(runs)
  run_assoc = get_run_assoc(results, run_ranges)
  dict_str = jinja2.Template(HLT_VSTRING if args.vstring else HLT_DICT).render(
    hlt_path    = results[0]['title'],
    int_lumi    = round(recorded_sum, 3),
    unprescaled = INT_LUMIS[era] <= recorded_sum,
    runs        = run_assoc,
  )
  print(dict_str)
