#!/usr/bin/env python

import json
import argparse
import os
import collections

def get_year(campaign_str):
  campaigns = [ '16', '17', '18' ]
  for campaign in campaigns:
    required = campaign
    required_inv = [ c for c in campaigns if c != campaign ]
    if required in campaign_str and not any(c in campaign_str for c in required_inv):
      return '20%s' % required
  raise ValueError('Unable to deduce campaign year for string: %s' % campaign_str)

def get_width(entries, key):
  return max(map(lambda x: len(x[key]) if key in x else 0, entries))

def write_datasets(entries, file_name):
  max_dbs_width = get_width(entries, 'dbs')
  max_category_width = get_width(entries, 'category')
  max_process_width = get_width(entries, 'process_name')
  max_loc_width = get_width(entries, 'loc')
  max_xs_head = max(map(lambda x: len(str(x['xs_value']).split('.')[0]), entries))
  max_xs_tail = max(map(lambda x: len(str(x['xs_value']).split('.')[1]), entries))

  refs = []
  for entry in entries:
    for xs_ref in entry['xs_refs']:
      if xs_ref not in refs:
        refs.append(xs_ref)

  last_comment = ''
  with open(file_name, 'w') as f:
    for entry in entries:
      entry['dbs_width'] = max_dbs_width
      entry['category_width'] = max_category_width
      entry['process_width'] = max_process_width
      entry['loc_width'] = max_loc_width

      xs_str = str(entry['xs_value'])
      xs_split = xs_str.split('.')
      xs_head_padding = max_xs_head - len(xs_split[0])
      xs_tail_padding = max_xs_tail - len(xs_split[1])
      entry['xs_head_padding'] = ' ' * xs_head_padding
      entry['xs_tail_padding'] = ' ' * xs_tail_padding

      entry['refs'] = ''.join(map(lambda y: '[%d]' % (y + 1), sorted(map(lambda x: refs.index(x), entry['xs_refs']))))
      if entry['refs']:
        entry['refs'] = ' ' + entry['refs']

      line = '{dbs:<{dbs_width}} {enabled} {category:<{category_width}} {process_name:<{process_width}} '.format(**entry)
      if entry['loc']:
        line += '{loc:<{loc_width}} '.format(**entry)
      line +='{xs_head_padding}{xs_value}{xs_tail_padding} # {xs_order}{refs}'.format(**entry)
      if entry['xs_comment']:
        line += '; {xs_comment}'.format(**entry)
      line += '\n'

      if entry['comment'] != last_comment:
        if last_comment:
          f.write('\n')
        last_comment = entry['comment']
        f.write('# {comment}\n'.format(**entry))
      f.write(line)

    f.write('\n# References:\n')
    for idx, ref in enumerate(refs):
      f.write('# [%d] %s\n' % (idx + 1, ref))


class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
  help = 'R|Input JSON file containing datasets',
)
parser.add_argument(
  '-o', '--output', dest = 'output', metavar = 'directory', required = False, type = str,
  #default = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test', 'datasets', 'txt'),
  default = os.path.join('test', 'datasets', 'txt'),
  help = 'R|Output directory where the dataset tables will be stored',
)
args = parser.parse_args()

input_filename = args.input
output_dirname = args.output

if not os.path.isdir(output_dirname):
  raise ValueError('No such directory: %s' % output_dirname)

with open(input_filename, 'r') as f:
  json_data = json.load(f)

table = collections.OrderedDict([
  ('mc',      collections.OrderedDict()),
  ('fast',    collections.OrderedDict()),
  ('private', collections.OrderedDict()),
])

eras_initialized = False

for category_entry in json_data:
  category = category_entry['category']
  for sample_entry in category_entry['samples']:
    sample_name = sample_entry['name']
    enabled = sample_entry['enabled']
    process = sample_entry['process']

    xs_value = sample_entry['xs']['value']
    xs_order = sample_entry['xs']['order']
    xs_comment = sample_entry['xs']['comment']
    xs_references = sample_entry['xs']['references']

    if xs_value > 1e6:
      xs_value = '%.3e' % xs_value

    if not eras_initialized:
      for era in sample_entry['datasets']:
          for mc_type in table:
            table[mc_type][era] = []
      eras_initialized = True

    for era in sample_entry['datasets']:
      for dataset_entry in sample_entry['datasets'][era]:
        dbs = dataset_entry['dbs']
        dataset_name = dataset_entry['alt'] if 'alt' in dataset_entry else sample_name
        location = dataset_entry['loc'] if 'loc' in dataset_entry else ''

        mc_type = 'mc'
        if dbs.endswith('/USER'):
          if 'fastsim' in dataset_name:
            mc_type = 'fast'
          else:
            mc_type = 'private'

        table[mc_type][era].append(
          collections.OrderedDict([
            ('dbs',          dbs),
            ('enabled',      enabled),
            ('category',     category),
            ('comment',      process),
            ('process_name', dataset_name),
            ('xs_value',     xs_value),
            ('xs_order',     xs_order),
            ('xs_refs',      xs_references),
            ('xs_comment',   xs_comment),
            ('loc',          location),
          ])
        )

for mc_type in table:
  for era in table[mc_type]:
    if not table[mc_type][era]:
      continue

    file_name_base = '{base}_{mc_type}_{year}_{campaign}'.format(
      base     = os.path.splitext(os.path.basename(input_filename))[0],
      mc_type  = mc_type if mc_type != 'private' else 'mc',
      year     = get_year(era),
      campaign = era,
    )
    if mc_type == 'private':
      file_name_base += '_{}'.format(mc_type)
    file_name_base += '.txt'

    file_name = os.path.join(output_dirname, file_name_base)
    write_datasets(table[mc_type][era], file_name)
