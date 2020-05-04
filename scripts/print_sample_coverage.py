#!/usr/bin/env python

import json
import re
import copy
import jinja2
import argparse
import os
import datetime

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
      .content {
        padding-bottom: 100px;
        display: inline-block;
        max-width: 1700px;
      }
    </style>
  </head>

  <body>
  <em>
      file automatically generated at {{ current_time }}
    </em>
   
   {% for table_set in table_sets %}
     <div class="content">
     {% for table in table_set %}
       {{ table }}
     {% endfor %}
     </div>
   {% endfor %}
  </body>
</html>
"""

table_template = """
<table style="width:250px; float: left">
  <tr>
    <th colspan="2" rowspan="2">resonant {{ decay_channel }}</th>
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

table_nonresonant_ggf_template = """
<table style="width:250px; float: left">
  <tr>
    <th>non-resonant ggf {{ decay_mode }}</th>
      {% for shape in shapes %}
        <th>{{ shape }}</th>
      {% endfor %}
  </tr>
  {% for entry in entries %}
    {{ entry }}
  {% endfor %}
  
</table>
"""

entry_nonresonant_ggf_template = """
{%- for era in eras -%}
  <tr>
      <td style="background-color: {% if loop.index % 3 == 0 %}#ffcccc{% elif loop.index % 3 == 1 %}#ccffcc{% else %}#ffffcc{% endif %}">{{ era }}</td>
      {%- for shape in shapes -%}
          <td {% if nonresonant_map[decay_channel][shape][era] %}class="pos">
            <a href="https://cmsweb.cern.ch/das/request?input={{ nonresonant_map[decay_channel][shape][era] }}">
              x
            </a>
          {% else %}class="neg">{% endif %}</td>
      {%- endfor -%}
  </tr> 
{%- endfor -%}
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

table_nonresonant_vbf_template = """
<table style="width:800px; float: left">
  <tr>
    <th colspan="3">non-resonant vbf {{ decay_channel }}</th>
    {% for era in eras %}
      <th>{{ era }}</th>
    {% endfor %}
  </tr>
  {% for cv in cvs %}
  {% set cv_loop = loop %}
  {% for c2v in c2vs %}
  {% set c2v_loop = loop %}
  {% for c3 in c3s %}
  {% set c3_loop = loop %}
    <tr>
      {% if c2v_loop.index == 1 and c3_loop.index == 1 %}
      <th rowspan="{{ c2vs|length * c3s|length }}">cv = {{ cv | replace("p",".") }}</th>
      {% endif %}
      {% if c3_loop.index == 1 %}
      <th rowspan="{{ c3s|length }}">c2v = {{ c2v | replace("p",".") }}</th>
      {% endif %}
      <th>c3 = {{ c3 | replace("p",".") }}</th>
      {% for era in eras %}
        <td {% if nonresonant_map[decay_channel][cv][c2v][c3][era] %}class="pos">
         <a href="https://cmsweb.cern.ch/das/request?input={{ nonresonant_map[decay_channel][cv][c2v][c3][era] }}">
           x
         </a>
        {% else %}class="neg">{% endif %}</td>
      {% endfor %} 
    </tr>
  {% endfor %}
  {% endfor %}
  {% endfor %}
</table>
"""

RR_PRODUCTION_MODE = 'production_mode'
RR_SPIN            = 'spin'
RR_MASS_POINT      = 'mass_point'
RR_DECAY_CHANNEL   = 'decay_channel'
RR_SHAPE           = 'shape'
RR_CV              = 'cv'
RR_C2V             = 'c2v'
RR_C3              = 'c3'

RESONANT_REGEX_PATTERN = r'signal_(?P<%s>(ggf|vbf))_spin(?P<%s>[0|2]{1})_(?P<%s>\d+)_hh_(?P<%s>[0-9A-Za-z_]+)' % (
  RR_PRODUCTION_MODE, RR_SPIN, RR_MASS_POINT, RR_DECAY_CHANNEL
)
RESONANT_REGEX = re.compile(RESONANT_REGEX_PATTERN)

NONRESONANT_GGF_REGEX_PATTERN = r'signal_ggf_nonresonant_node_(?P<%s>(SM|sm|box|\d+))_hh_(?P<%s>[0-9A-Za-z_]+)' % (
  RR_SHAPE, RR_DECAY_CHANNEL
)
NONRESONANT_GGF_REGEX = re.compile(NONRESONANT_GGF_REGEX_PATTERN)

NONRESONANT_VBF_REGEX_PATTERN = r'signal_vbf_nonresonant_(?P<%s>(\d+(p\d+)?))_(?P<%s>(\d+(p\d+)?))_(?P<%s>(\d+(p\d+)?))_hh_(?P<%s>[0-9A-Za-z_]+)' % (
  RR_CV, RR_C2V, RR_C3, RR_DECAY_CHANNEL
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
  nonresonant_map_ggf_agg = { name : [] for name in [ 'decay_channel', 'shape' ] }
  nonresonant_map_vbf_agg = { name: [] for name in [ 'decay_channel', 'cv', 'c2v', 'c3' ] }

  add_to_resonant_map_agg = lambda key, value: add_to_map(resonant_map_agg, key, value)
  add_to_nonresonant_ggf_agg = lambda key, value: add_to_map(nonresonant_map_ggf_agg, key, value)
  add_to_nonresonant_vbf_agg = lambda key, value: add_to_map(nonresonant_map_vbf_agg, key, value)

  for e in j:
    for sample in e['samples']:
      c = sample['name']
      s = { camp : sample['datasets'][camp][0]['dbs'] if sample['datasets'][camp] else '' for camp in required }

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

      elif m_nonres_ggf:
        shape           = m_nonres_ggf.group(RR_SHAPE)
        decay_channel   = m_nonres_ggf.group(RR_DECAY_CHANNEL)

        if decay_channel not in nonresonant_map_ggf:
          nonresonant_map_ggf[decay_channel] = {}
        nonresonant_map_ggf[decay_channel][shape] = copy.deepcopy(s)

        add_to_nonresonant_ggf_agg('decay_channel', decay_channel)
        add_to_nonresonant_ggf_agg('shape', shape)
      elif m_nonres_vbf:
        decay_channel   = m_nonres_vbf.group(RR_DECAY_CHANNEL)
        cv              = m_nonres_vbf.group(RR_CV)
        c2v             = m_nonres_vbf.group(RR_C2V)
        c3              = m_nonres_vbf.group(RR_C3)

        if 'p' not in cv:
          cv += 'p0'
        if 'p' not in c2v:
          c2v += 'p0'
        if 'p' not in c3:
          c3 += 'p0'

        if decay_channel not in nonresonant_map_vbf:
          nonresonant_map_vbf[decay_channel] = {}
        if cv not in nonresonant_map_vbf[decay_channel]:
          nonresonant_map_vbf[decay_channel][cv] = {}
        if c2v not in nonresonant_map_vbf[decay_channel][cv]:
          nonresonant_map_vbf[decay_channel][cv][c2v] = {}
        nonresonant_map_vbf[decay_channel][cv][c2v][c3] = copy.deepcopy(s)

        add_to_nonresonant_vbf_agg('decay_channel', decay_channel)
        add_to_nonresonant_vbf_agg('cv', cv)
        add_to_nonresonant_vbf_agg('c2v', c2v)
        add_to_nonresonant_vbf_agg('c3', c3)

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
            resonant_map[decay_channel][production_mode][spin][mass_point] = { camp : '' for camp in required }

  for decay_channel in nonresonant_map_ggf_agg['decay_channel']:
    if decay_channel not in nonresonant_map_ggf:
      nonresonant_map_ggf[decay_channel] = {}
    for shape in nonresonant_map_ggf_agg['shape']:
      if shape not in nonresonant_map_ggf[decay_channel]:
        nonresonant_map_ggf[decay_channel][shape] = { camp : '' for camp in required }

  for coupling in [ 'cv', 'c2v', 'c3' ]:
    #for val in [ '0p5', '1p0', '1p5', '2p0' ]:
    #  add_to_nonresonant_vbf_agg(coupling, val)
    nonresonant_map_vbf_agg[coupling] = sorted(
      nonresonant_map_vbf_agg[coupling],
      key = lambda val: float(val.replace('p', '.'))
    )
  for decay_channel in nonresonant_map_vbf_agg['decay_channel']:
    if decay_channel not in nonresonant_map_vbf:
      nonresonant_map_vbf[decay_channel] = {}
    for cv in nonresonant_map_vbf_agg['cv']:
      if cv not in nonresonant_map_vbf[decay_channel]:
        nonresonant_map_vbf[decay_channel][cv] = {}
      for c2v in nonresonant_map_vbf_agg['c2v']:
        if c2v not in nonresonant_map_vbf[decay_channel][cv]:
          nonresonant_map_vbf[decay_channel][cv][c2v] = {}
        for c3 in nonresonant_map_vbf_agg['c3']:
          if c3 not in nonresonant_map_vbf[decay_channel][cv][c2v]:
            nonresonant_map_vbf[decay_channel][cv][c2v][c3] = { camp : '' for camp in required }

  tables_nonres_vbf = []
  for decay_channel in nonresonant_map_vbf_agg['decay_channel']:
    table_nonres_vbf = jinja2.Template(table_nonresonant_vbf_template).render(
      eras = required,
      decay_channel = decay_channel,
      cvs = nonresonant_map_vbf_agg['cv'],
      c2vs = nonresonant_map_vbf_agg['c2v'],
      c3s = nonresonant_map_vbf_agg['c3'],
      nonresonant_map = nonresonant_map_vbf,
    )
    tables_nonres_vbf.append(table_nonres_vbf)

  tables_nonres_ggf = []
  for decay_channel in nonresonant_map_ggf_agg['decay_channel']:
    entries = []
    entry = jinja2.Template(entry_nonresonant_ggf_template).render(
      eras = required,
      decay_channel = decay_channel,
      shapes = nonresonant_map_ggf_agg['shape'],
      nonresonant_map = nonresonant_map_ggf,
    )
    entries.append(entry)
    table = jinja2.Template(table_nonresonant_ggf_template).render(
      decay_mode = decay_channel,
      entries = entries,
      shapes = nonresonant_map_ggf_agg['shape'],
    )
    tables_nonres_ggf.append(table)

  tables_res = []
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
    tables_res.append(table)

  return tables_res, tables_nonres_ggf, tables_nonres_vbf

if __name__ == '__main__':
  basedir = os.path.join(os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test', 'datasets', 'json',)
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

  tables_res, tables_nonres_ggf, tables_nonres_vbf = [], [], []
  for fn in args.input:
    if not os.path.isfile(fn):
      raise ValueError("No such file: %s" % fn)
    res, nonres_ggf, nonres_vbf = get_tables(fn, args.eras)
    tables_res.extend(res)
    tables_nonres_ggf.extend(nonres_ggf)
    tables_nonres_vbf.extend(nonres_vbf)

  html = jinja2.Template(html_template).render(
    table_sets = [ tables_res, tables_nonres_ggf, tables_nonres_vbf ],
    current_time = str(datetime.datetime.now()),
  )

  with open(args.output, 'w') as f:
    f.write(html)
