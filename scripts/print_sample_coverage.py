#!/usr/bin/env python

import json
import re
import copy
import jinja2
import argparse
import os

html_template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">

    <title>Sample coverage in Run2</title>
    <meta name="description" content="Sample coverage in Run2">
  
    <style>
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
      }
      td { background: white; }
      td.pos {
        background-color: green;
      }
      td.neg {
        background-color: red;
      }
      td a {
          display:block;
          width:100%;
          color: green;
      }
    </style>
  </head>

  <body>
   
   <div>
   {% for table in tables %}
     {{ table }}
   {% endfor %}
   </div>
  </body>
</html>
"""

table_template = """
<table style="width:300px; float: left">
  <tr>
    <th colspan="2" rowspan="2">{{ decay_channel }}</th>
    {% for production_mode in production_modes %}
      <th colspan="{{ spins|length }}">{{ production_mode }}</th>
    {% endfor %}
  </tr>
  <tr>
    {% for production_mode in production_modes %}
      {% for spin in spins %}
        <th>{{ spin }}</th>
      {% endfor %}
    {% endfor %}
  </tr>
  {% for entry in entries %}
    {{ entry }}
  {% endfor %}
</table>
"""

entry_template = """
{%- for era in eras -%}
  <tr>
      {%- if loop.index == 1 -%}
        <td rowspan="{{eras|length}}" style="background: #{% if is_odd %}CCC{% else %}FFF{% endif %}">{{ masspoint }}</td>        
      {%- endif -%}
      <td style="background-color: {% if loop.index % 3 == 0 %}#ffcccc{% elif loop.index % 3 == 1 %}#ccffcc{% else %}#ffffcc{% endif %}">{{ era }}</td>
      {%- for production_mode in production_modes -%}
        {%- for spin in spins -%}
          <td {% if resonant_map[decay_channel][production_mode][spin][masspoint][era] %}class="pos">
            <a href="https://cmsweb.cern.ch/das/request?input={{ resonant_map[decay_channel][production_mode][spin][masspoint][era] }}">
              x
            </a>
          {% else %}class="neg">{% endif %}</td>
        {%- endfor -%}
      {%- endfor -%}
  </tr> 
{%- endfor -%}
"""

RR_PRODUCTION_MODE = 'production_mode'
RR_SPIN            = 'spin'
RR_MASS_POINT      = 'mass_point'
RR_DECAY_CHANNEL   = 'decay_channel'
RR_SHAPE           = 'shape'
RR_CV              = 'cv'
RR_C2V             = 'c2v'
RR_C3              = 'c3'

RESONANT_REGEX_PATTERN = r'signal_(?P<%s>(ggf|vbf))_spin(?P<%s>[0|2]{1})_(?P<%s>\d+)_hh_(?P<%s>[0-9A-Za-z]+)' % (
  RR_PRODUCTION_MODE, RR_SPIN, RR_MASS_POINT, RR_DECAY_CHANNEL
)
RESONANT_REGEX = re.compile(RESONANT_REGEX_PATTERN)

NONRESONANT_GGF_REGEX_PATTERN = r'signal_ggf_nonresonant_node_(?P<%s>(SM|sm|box|\d+))_hh_(?P<%s>[0-9A-Za-z]+)' % (
  RR_SHAPE, RR_DECAY_CHANNEL
)
NONRESONANT_GGF_REGEX = re.compile(NONRESONANT_GGF_REGEX_PATTERN)

NONRESONANT_VBF_REGEX_PATTERN = r'signal_vbf_nonresonant_(?P<%s>(\d+(p\d+)?))_(?P<%s>(\d+(p\d+)?))_(?P<%s>(\d+(p\d+)?))_hh_(?P<%s>[0-9A-Za-z]+)' % (
  RR_DECAY_CHANNEL, RR_CV, RR_C2V, RR_C3
)
NONRESONANT_VBF_REGEX = re.compile(NONRESONANT_VBF_REGEX_PATTERN)

class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def add_to_map(m, key, value):
  if value not in m[key]:
    m[key].append(value)

def get_tables(fn, required):
  with open(fn, 'r') as f:
    j = json.load(f)

  resonant_map = {}
  nonresonant_map_ggf = {}
  nonresonant_map_vbf = {}

  resonant_map_agg = { name : [] for name in [ 'decay_channel', 'spin', 'production_mode', 'mass_point' ] }

  add_to_resonant_map_agg = lambda key, value: add_to_map(resonant_map_agg, key, value)

  for e in j:
    c = e['category']
    s = { camp : e['samples'][0]['datasets'][camp][0]['dbs'] if e['samples'][0]['datasets'][camp] else '' for camp in required }

    m_res        = RESONANT_REGEX.match(c)
    m_nonres_ggf = NONRESONANT_GGF_REGEX.match(c)
    m_nonres_vbf = NONRESONANT_VBF_REGEX.match(c)

    if m_res:
      production_mode = m_res.group(RR_PRODUCTION_MODE)
      spin            = int(m_res.group(RR_SPIN))
      mass_point      = int(m_res.group(RR_MASS_POINT))
      decay_channel   = m_res.group(RR_DECAY_CHANNEL)

      if decay_channel not in resonant_map:
        resonant_map[decay_channel] = {}
      if production_mode not in resonant_map[decay_channel]:
        resonant_map[decay_channel][production_mode] = {}
      if spin not in resonant_map[decay_channel][production_mode]:
        resonant_map[decay_channel][production_mode][spin] = {}
      resonant_map[decay_channel][production_mode][spin][mass_point] = copy.deepcopy(s)

      add_to_resonant_map_agg('decay_channel', decay_channel)
      add_to_resonant_map_agg('spin', spin)
      add_to_resonant_map_agg('production_mode', production_mode)
      add_to_resonant_map_agg('mass_point', mass_point)

      #print('production = {} ; spin = {} ; mass = {} ; channel = {} ; {}'.format(
      #  production_mode, spin, mass_point, decay_channel, ', '.join([ '%s -> %s' % x for x in s.items()]),
      #))
    elif m_nonres_ggf:
      production_mode = 'ggf'
      shape           = m_nonres_ggf.group(RR_SHAPE)
      decay_channel   = m_nonres_ggf.group(RR_DECAY_CHANNEL)

      #print('production = {} ; shape = {} ; channel = {} ; {}'.format(
      #  production_mode, shape, decay_channel, ', '.join([ '%s -> %s' % x for x in s.items()]),
      #))
    elif m_nonres_vbf:
      production_mode = "vbf"
      decay_channel   = m_nonres_vbf.group(RR_DECAY_CHANNEL)
      cv              = m_nonres_vbf.group(RR_CV)
      c2v             = m_nonres_vbf.group(RR_C2V)
      c3              = m_nonres_vbf.group(RR_C3)

      #print('production = {}; channel = {} ; cv = {} ; c2v = {} ; c3 = {} ; {}'.format(
      #  production_mode, decay_channel, cv, c2v, c3, ', '.join(['%s -> %s' % x for x in s.items()]),
      #))
    else:
      raise RuntimeError("Invalid category: %s" % c)

  resonant_map_agg['mass_point'] = sorted(resonant_map_agg['mass_point'])

  add_to_resonant_map_agg('production_mode', 'vbf')
  for decay_channel in resonant_map_agg['decay_channel']:
    if decay_channel not in resonant_map:
      resonant_map[decay_channel] = {}
    for production_mode in resonant_map_agg['production_mode']:
      if production_mode not in resonant_map[decay_channel]:
        resonant_map[decay_channel][production_mode] = {}
      for spin in resonant_map_agg['spin']:
        if spin not in resonant_map[decay_channel][production_mode]:
          resonant_map[decay_channel][production_mode][spin] = {}
        for mass_point in resonant_map_agg['mass_point']:
          if mass_point not in resonant_map[decay_channel][production_mode][spin]:
            resonant_map[decay_channel][production_mode][spin][mass_point] = { camp : False for camp in required }

  tables = []
  for decay_channel in resonant_map_agg['decay_channel']:
    entries = []
    for idx, mass_point in enumerate(resonant_map_agg['mass_point']):
      entry = jinja2.Template(entry_template).render(
        eras = required,
        masspoint = mass_point,
        production_modes = resonant_map_agg['production_mode'],
        spins = resonant_map_agg['spin'],
        resonant_map = resonant_map,
        decay_channel = decay_channel,
        is_odd = (idx % 2 == 1),
      )
      entries.append(entry)

    table = jinja2.Template(table_template).render(
      decay_channel = decay_channel,
      production_modes = resonant_map_agg['production_mode'],
      spins = resonant_map_agg['spin'],
      entries = entries,
    )
    tables.append(table)

  return tables

if __name__ == '__main__':
  #basedir = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test', 'datasets', 'json',)
  basedir = os.path.join('test', 'datasets', 'json')

  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  parser.add_argument(
    '-i', '--input', dest = 'input', metavar = 'file', required = False, type = str, nargs = '+',
    default = [
      os.path.join(basedir, 'datasets_hh_multilepton.json'),
      os.path.join(basedir, 'datasets_hh_bbww.json'),
    ],
    help = 'R|Input JSON files',
  )
  parser.add_argument(
    '-o', '--output', dest = 'output', metavar = 'file', required = False, type = str, default = 'coverage.html',
    help = 'R|Output file name',
  )
  parser.add_argument(
    '-e', '--eras', dest = 'eras', metavar = 'era', required = False, type = str, nargs = '+',
    default = [ "RunIISummer16MiniAODv3", "RunIIFall17MiniAODv2", "RunIIAutumn18MiniAOD" ],
    help = 'R|Eras to consider in the output',
  )
  args = parser.parse_args()

  tables = []
  for fn in args.input:
    if not os.path.isfile(fn):
      raise ValueError("No such file: %s" % fn)
    tables.extend(get_tables(fn, args.eras))

  html = jinja2.Template(html_template).render(
    tables = tables,
  )

  with open(args.output, 'w') as f:
    f.write(html)
