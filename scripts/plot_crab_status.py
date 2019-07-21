#!/usr/bin/env python

import os
import datetime
import argparse
import logging
import sys
import re
import copy
import base64
import jinja2
import tempfile

import matplotlib.dates as mdates
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
  mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np

html_template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">

    <title>CRAB progress</title>
    <meta name="description" content="CRAB progress">

    <style>
    </style>
  </head>

  <body>
  <em>
      file automatically generated at {{ current_time }}
    </em>

   <div>
   {% for image in images %}
     <div style="display: inline-block; width: 500px; margin-left: 30px; overflow-wrap: break-word;">
       <p>{{ image[0] }}</p>
       <img src="data:image/png;base64, {{ image[1] }}" />
     </div>
   {% endfor %}
   </div>
  </body>
</html>
"""

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

  current_datetime = None
  for line in lines:
    if line.startswith('INFO'):
      datetime_str = ' '.join(line.rstrip('\n').split()[1:]).split(',')[0]
      current_datetime = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
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

  if nof_jobs < 0:
    assert(not parsed)
  return parsed, current_datetime

def plot_pie(all_states, output, nof_tasks, nof_completed_tasks, title):
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

  ax.set_title(
    "{}{} jobs in {} tasks ({} completed)".format('%s: ' % title if title else '',  tot, nof_tasks, nof_completed_tasks)
  )

  plt.savefig(output, bbox_inches = 'tight')
  logging.info("Saved figure to: {}".format(output))
  plt.close()

def plot_progress(data):
  all_states = list({state for entry in data for state in entry[0].keys()})
  available_dates = list(sorted(d[1] for d in data))

  current_date = datetime.datetime.now()
  first_date = available_dates[0] if available_dates else current_date
  first_date = first_date.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

  difference_in_days = (current_date - first_date).days
  data_augmented = {
    first_date + datetime.timedelta(days = days_passed) : {
      'recorded_date' : None,
      'data' : {}
    } for days_passed in range(difference_in_days + 1)
  }

  for entry in data:
    entry_data = entry[0]
    entry_date = entry[1]
    date_found = False
    for date_candidate in data_augmented:
      if  date_candidate.day == entry_date.day and \
          date_candidate.month == entry_date.month and \
          date_candidate.year == entry_date.year:
        if data_augmented[date_candidate]['recorded_date'] and \
           entry_date < data_augmented[date_candidate]['recorded_date']:
          continue
        data_augmented[date_candidate]['recorded_date'] = entry_date
        data_augmented[date_candidate]['data'] = { state : 0 for state in all_states }
        for state in entry_data:
          data_augmented[date_candidate]['data'][state] = entry_data[state]
        date_found = True
    assert(date_found)

  prev_date = None
  dates_sorted = sorted(data_augmented.keys())
  for date in dates_sorted:
    if not data_augmented[date]['recorded_date']:
      if not prev_date:
        assert(len(dates_sorted) == 1)
        continue
      data_augmented[date]['data'] = copy.deepcopy(data_augmented[prev_date]['data'])
      data_augmented[date]['recorded_date'] = copy.deepcopy(data_augmented[prev_date]['recorded_date'])
    prev_date = date

  data_to_plot = []
  for state in all_states:
    data_to_plot_row = []
    for date in dates_sorted:
      data_to_plot_row.append(data_augmented[date]['data'][state])
    data_to_plot.append(data_to_plot_row)

  plt.figure(figsize = (5.5, 3.5))
  plt.ylabel('Number of CRAB jobs')
  if prev_date:
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.stackplot(dates_sorted, data_to_plot, colors = [ COLMAP[state] for state in all_states ], labels = all_states)
    plt.gcf().autofmt_xdate()
    plt.legend(loc = 'upper left', fontsize = 10)
    plt.gca().set_xticks(plt.gca().get_xticks()[::2])
    plt.gca().tick_params(axis = 'both', labelsize = 10)

    nof_jobs = sum(col[-1] for col in data_to_plot)
    plt.ylim(0, nof_jobs)

  tmp_image = tempfile.TemporaryFile(suffix = 'png')
  plt.savefig(tmp_image, bbox_inches = 'tight', format = 'png')
  plt.close()

  tmp_image.seek(0)
  encoded_image = base64.b64encode(tmp_image.read())
  tmp_image.close()

  return encoded_image, first_date

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
    '-t', '--title', dest = 'title', metavar = 'text', required = False, type = str, default = '',
    help = 'R|Additional title to the plot',
  )
  parser.add_argument(
    '-P', '--progress', dest = 'progress', metavar = 'file', required = False, type = str, default = '',
    help = 'R|HTML file showing the progress of each CRAB task',
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

  in_dir   = args.input
  pattern  = re.compile(args.pattern)
  output   = args.output
  title    = args.title
  progress = os.path.abspath(args.progress)

  lines = {}
  for subdir in os.listdir(in_dir):
    if subdir not in lines:
      lines[subdir] = []

    subdir_fp = os.path.join(in_dir, subdir)
    if not pattern.match(subdir):
      logging.debug("Skipping directory {} because it does not match the required pattern".format(subdir_fp))
      continue
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
          if lines_to_parse:
            parsed_lines, parsed_datetime = parse_lines(lines_to_parse)
            if parsed_lines and parsed_datetime:
              lines[subdir].append((parsed_lines, parsed_datetime))
          lines_to_parse = []
          record = True
        elif line_stripped.startswith(
              'No publication information (publication has been disabled in the CRAB configuration file)'
            ):
          record = False
        if record:
          lines_to_parse.append(line_stripped)

    if lines[subdir]:
      latest_entry = lines[subdir][-1]
      parsed_lines = latest_entry[0]
      parsed_datetime = latest_entry[1]
      logging.debug("Task {} ({}): {}".format(
        subdir, parsed_datetime.isoformat(), ', '.join(list(map(lambda kv: '%s -> %d' % kv, parsed_lines.items())))
      ))
    else:
      logging.error("No job statistics for task: {}".format(subdir))

  if progress:
    progress_dir = os.path.dirname(progress)
    if not os.path.isdir(progress_dir):
      raise ValueError("No such directory: %s" % progress_dir)

    encoded_images = []
    for subdir in sorted(lines.keys()):
      encoded_image, first_date = plot_progress(lines[subdir])
      encoded_images.append((subdir, encoded_image, first_date))
    encoded_images = list(sorted(encoded_images, key = lambda entry: entry[2]))

    with open(progress, 'w') as progress_file:
      html = jinja2.Template(html_template).render(
        images = encoded_images,
        current_time = str(datetime.datetime.now()),
      )
      progress_file.write(html)

  nof_completed_tasks = len(
    filter(lambda kv: len(kv[1]) > 0 and len(kv[1][-1][0]) == 1 and 'finished' in kv[1][-1][0], lines.items())
  )
  all_states = {}
  for subdir, all_lines in lines.items():
    if not all_lines:
      continue
    lines_to_parse = all_lines[-1][0]
    for state, values in lines_to_parse.items():
      if state not in all_states:
        all_states[state] = 0
      all_states[state] += values

  all_states_sorted = sorted(all_states.items(), key = lambda kv: kv[1], reverse = True)
  plot_pie(all_states_sorted, output, len(lines), nof_completed_tasks, title)
