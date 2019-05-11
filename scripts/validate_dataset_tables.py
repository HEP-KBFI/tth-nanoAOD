#!/usr/bin/env python

import argparse
import os.path

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def raiseError(buffer, msg):
  print('\n'.join(buffer))
  raise RuntimeError(msg)

def validate(fn, unique_category = False):
  if not os.path.isfile(fn):
    raise ValueError("No such file: %s" % fn)

  print("{line} VALIDATING {fn} {line}".format(line = "=" * 20, fn = fn))
  era = os.path.splitext(os.path.basename(fn))[0].split('_')[-1]
  assert(era.startswith('RunII'))

  miniaods, process_names, category_names = [], [], []
  buffer = []
  with open(fn, 'r') as f:
    for line in f:
      line_stripped = line.rstrip('\n')

      if not line_stripped or line_stripped.startswith('#'):
        continue
      buffer.append(line_stripped)

      line_split = line_stripped.split()

      miniaod = line_split[0]
      if not miniaod.endswith('/MINIAODSIM'):
        raiseError(buffer, "Line not ending with '/MINIAODSIM'")
      if miniaod in miniaods:
        raiseError(buffer, "{} listed twice".format(miniaod))

      miniaods.append(miniaod)
      miniaod_split = miniaod.split('/')[1:]
      miniaod_era = miniaod_split[1].split('-')[0]
      if miniaod_era != era:
        raiseError(buffer, "Expected era '{}', got '{}'".format(era, miniaod_era))

      process_name = line_split[3]
      if process_name in process_names:
        raiseError(buffer, "Detected same process name twice: {}".format(process_name))
      process_names.append(process_name)

      if unique_category:
        category_name = line_split[3]
        if category_name in category_names:
          raiseError(buffer, "Detected same category name twice: {}".format(category_name))
        category_names.append(category_name)

  print("No errors found in {}".format(fn))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  parser.add_argument(
    '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
    help = 'R|Input JSON file containing datasets',
  )
  parser.add_argument(
    '-c', '--category-unique', dest = 'caregory_unique', action = 'store_true', default = False,
    help = 'R|Require unique category names',
  )
  args = parser.parse_args()

  validate(args.input, args.caregory_unique)
