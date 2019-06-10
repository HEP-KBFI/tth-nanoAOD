#!/usr/bin/env python

import os
import datetime
import argparse
import logging
import sys
import re

import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
  mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

COLMAP = {
  'finished'     : '#49a328',
  'idle'         : '#e4ea7e',
  'failed'       : '#c63611',
  'running'      : '#56d2ff',
  'unsubmitted'  : '#b3b4b5',
  'cooloff'      : '#ffbfff',
  'transferring' : '#9bea7e',
  'killed'       : '#420d0d',
  'held'         : '#f442b3',
}

CRAB_LOG_FN = 'crab.log'

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def parse_lines(lines):
  parsed = {}
  nof_jobs = -1

  for line in lines:
    line_split = line.replace('(', '').replace(')', '').split()
    if len(line_split) < 5:
      continue

    state = line_split[-3]
    counts = list(map(int, line_split[-1].split('/')))
    parsed[state] = counts[0]

    if nof_jobs < 0:
      nof_jobs = counts[1]
    else:
      assert(nof_jobs == counts[1])

  assert(sum(parsed.values()) == nof_jobs)
  return parsed

def plot(all_states, output, nof_tasks, nof_completed_tasks):
  vals   = list(map(lambda kv: kv[1], all_states))
  labels = list(map(lambda kv: kv[0], all_states))
  cols   = list(map(lambda lab: COLMAP[lab], labels))

  tot = sum(vals)
  legend_labels = list(map(lambda kv: '%s %.2f%%' % (kv[0], 100. * kv[1] / tot), all_states))

  fig, ax = plt.subplots(figsize = (10, 8), subplot_kw = dict(aspect = "equal"))
  wedges, texts = ax.pie(vals, startangle = 60, colors = cols)

  bbox_props = dict(boxstyle = "square,pad=0.3", fc = "w", ec = "k", lw = 0.72)
  kw = dict(arrowprops = dict(arrowstyle = "-"), bbox = bbox_props, zorder = 0, va = "center", fontsize = 12)

  for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1) / 2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))

    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({ "connectionstyle" : connectionstyle })

    ax.annotate(
      str(vals[i]), xy = (x, y), xytext = (1.35 * np.sign(x), 1.4 * y), horizontalalignment = horizontalalignment, **kw
    )
  plt.legend(
    wedges, legend_labels, loc = 'lower left', title = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
    prop = { 'size' : 12 },
  )

  ax.set_title("%d jobs in %d tasks (%d completed)" % (tot, nof_tasks, nof_completed_tasks))

  plt.savefig(output, bbox_inches = 'tight')
  logging.info("Saved figure to: {}".format(output))
  plt.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  parser.add_argument(
    '-i', '--input', dest = 'input', metavar = 'directory', required = False, type = str,
    default = os.path.expanduser('~/crab_projects'),
    help = 'R|Directory containing CRAB status output',
  )
  parser.add_argument(
    '-p', '--pattern', dest = 'pattern', metavar = 'regex', required = False, type = str, default = '.*',
    help = 'R|Pattern of CRAB tasks',
  )
  parser.add_argument(
    '-o', '--output', dest = 'output', metavar = 'file', required = False, type = str, default = 'crab_status.png',
    help = 'R|Output image',
  )
  parser.add_argument(
    '-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
    help = 'R|Enable verbose printout',
  )
  args = parser.parse_args()

  logging.basicConfig(
    stream = sys.stdout,
    level  = logging.DEBUG if args.verbose else logging.INFO,
    format = '%(asctime)s - %(levelname)s: %(message)s',
  )

  in_dir  = args.input
  pattern = re.compile(args.pattern)
  output  = args.output

  lines = {}
  for subdir in os.listdir(in_dir):
    subdir_fp = os.path.join(in_dir, subdir)
    if not pattern.match(subdir):
      logging.debug("Skipping directory {} because it does not match the required pattern".format(subdir_fp))
    if not os.path.isdir(subdir_fp):
      continue
    crab_log = os.path.join(subdir_fp, CRAB_LOG_FN)
    if not os.path.isfile(crab_log):
      logging.warning("Could not find file {} in directory {}".format(CRAB_LOG_FN, subdir_fp))
      continue

    lines_to_parse = []
    record = False
    with open(crab_log, 'r') as crab_file:
      for line in crab_file:
        line_stripped = line.rstrip('\n')
        if line_stripped.startswith('Jobs status:'):
          lines_to_parse = []
          record = True
        elif line_stripped.startswith(
              'No publication information (publication has been disabled in the CRAB configuration file)'
            ):
          record = False
        if record:
          lines_to_parse.append(line_stripped)
    lines[subdir] = parse_lines(lines_to_parse)
    logging.debug("Task {}: {}".format(subdir, ', '.join(list(map(lambda kv: '%s -> %d' % kv, lines[subdir].items())))))

  nof_completed_tasks = len(filter(lambda kv: len(kv[1]) == 1 and 'finished' in kv[1], lines.items()))
  all_states = {}
  for subdir, lines_to_parse in lines.items():
    for state, values in lines_to_parse.items():
      if state not in all_states:
        all_states[state] = 0
      all_states[state] += values

  all_states_sorted = sorted(all_states.items(), key = lambda kv: kv[1], reverse = True)
  plot(all_states_sorted, output, len(lines), nof_completed_tasks)
