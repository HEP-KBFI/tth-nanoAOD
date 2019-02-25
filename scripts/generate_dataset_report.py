#!/usr/bin/env python

import json
import jinja2
import datetime
import argparse
import os

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">

    <title>Datasets in Run2</title>
    <meta name="description" content="Datasets in Run2">
  
    <style>
      a {color:#000000;}
      a:visited {color:#000000;}
      a:hover {color:#000000;}
      a:active {color:#000000;}
      a {
        text-decoration: none;
      }
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 15px;
        text-align: left;
        border-spacing: 5px;
      }
      table {
        margin-top: 50px;
        width:auto !important; 
        max-width: 70%; 
        min-width: 1200px;
      }
      .pass, .passx2 {
        background-color:#95E8A9;
      }
      .passx2 {
        color: green;
      }
      .fail, .failx2 {
        background-color:#E8A495;
      }
      .failx2 {
        color: red;
      }
      caption {
        text-align: left;
        background-color: #FFFC99;
      }
      .caption_text {
        font-size: 20px;
        font-weight: bold;
        color: black;
        text-decoration: none;
      }
      #toc_container {
        display: table;
        width: auto;
      }
      #toc_container, #toc_container ul, #toc_container ul li{
        list-style: outside none none !important;
        margin-left: 0px;
      }
      p.cat {
        margin-bottom:40px; 
        margin-top:40px; 
      }
      .category_style {
         font-size: 30px;
         font-weight: bold;
         text-decoration: none;
         color: black;
      }
      tab {
        display: inline-block; 
        margin-left: 10px; 
      }
      li.not_ok, li.ok {
          list-style-type: none;
          position: relative;
      }
      li.not_ok::before, li.ok::before {
          position: absolute;
          left: -0.8em;
          font-size: 1.1em;
      }
      li.not_ok::before {
        content: '\\2716';
        color: red;
      }
      li.ok::before {
        content: '\\2714';
        color: green;
      }
      li.cat::before {
        content: '\\2022\\2009';
        color: black;
      }
      .dbs {
        font-family:monospace;
        font-size: 14px;
      }
      .links {
        float:right;
        margin-left: 20px;
      }
      a.link, #toggle {
        color: blue;
        text-decoration: underline;
        cursor: pointer;
      }
      .sub_cat_box {display: none;}
    </style>
    <script>
    function toggleChildren(id) {
  
      var elem = document.getElementById(id);
      if(!elem) alert("error: not found!");
      else {
  
          if(elem.style.display == "block")
          {
            elem.style.display = "none";
          }
          else
          {
            elem.style.display = "block";
          }
      }
    }
    </script>
  </head>

  <body>
    <a name="top"></a>
    <em>
      file automatically generated at {{ current_time }}
    </em>
    
    {{toc}}
    
    {{summary}}
    
    {{ tables }}
    
  </body>
</html>
"""

TABLE_TEMPLATE = """
<table>
  <caption>
    <a name="{{ sample_name }}">
      <a href="#{{ sample_name }}" class="caption_text">
        {{ sample_name }}
      </a>
    </a> 
    <span class="up_button" style="float:right">
      [
      <a href="#top" class="link">
        up
      </a>
      ]
    </span>
  </caption>
  {% for table_row in table_rows %}
    {{ table_row }}
  {% endfor %}
</table>

<span style="font-size:20px;">
  Cross section: {{xs}} pb{% if order %} @ {{order}}{% endif %}
  [{%- for ref in refs -%}
    <a href="{{ref}}" class="link">{{loop.index}}</a>
    {%- if loop.index < refs|length %}, {% endif -%}
  {%- endfor -%}
  
  {%- if comment -%}
    {%- if refs|length > 0 -%}; 
    {%- endif -%}
    <em>
      {{comment}}
    </em>
  {%- endif -%}]
</span>
"""

ROW_TEMPLATE = """
{% if datasets|length > 0 %}
  {% for dataset in datasets %}
    <tr>
      {% if loop.index == 1 %}
        <th class="pass{% if is_important %}x2{% endif %}" rowspan="{{datasets|length}}">{{era}}</th>
      {% endif %}
      <td>
        <span class="dbs">
          {{dataset[0]}}
        </span>
        <span class="links">
          {% if not dataset[0].endswith('/USER') %}
            [
            <a class="link" href="https://cmsweb.cern.ch/das/request?input={{dataset[0]}}">
              DAS
            </a>]
            [
            <a class="link" href="https://cms-pdmv.cern.ch/mcm/requests?produce={{dataset[0]}}">
              PdmV
            </a>
            ]
          {% else %}
              [privately produced {% if dataset[1] %}FastSim{% else %}FullSim{% endif %} sample]
          {% endif %}
        </span>
      </td>
    </tr>
  {% endfor %}
{% else %}
  <tr>
    <th class="fail{% if is_important %}x2{% endif %}">
      {{era}}
    </th>
    <td>
      -
    </td>
  </tr>
{% endif %}
"""

HEADING_TEMPLATE = """
<p class="cat">
  <a name="{{category_name}}">
    <a href="#{{category_name}}"  class="category_style">
      {{category_name}}
    </a>
  </a>
  <tab>
  [
  <a href="#top" class="link">
    up
  </a>
  ]
</p>
"""

TOC_TEMPLATE = """
<div id="toc_container">
  <p style="font-size: 20px;">
    Sample completion
  </p>
  <ul>
    {% for category in categories %}
    <li class="cat">
      <a href="#{{ category['name'] }}" style="font-size: 1.2em;">
        {{ category['name'] }}
      </a> 
      ({{ category['nof_ok'] }}/{{ category['samples']|length }})
      <tab>
      [
      <span onclick="javascript: toggleChildren('category_id{{loop.index}}');" id="toggle">
        toggle
      </span>
      ]
    </li>
    <div id="category_id{{loop.index}}" class="sub_cat_box">
      <ul>
        {% for sample_data in category['samples'] %}
        <li class="{% if sample_data['is_ok'] %}ok{% else %}not_ok{% endif %}">
          <a href="#{{ sample_data['name'] }}">
            {{ sample_data['name'] }}
          </a>
        </li>
        {% endfor %}
      </ul>
    </div>
    {% endfor %}
  </ul>
</div>
"""

SUMMARY_TEMPLATE = """
<div>
  <p style="font-size: 20px;">
    Missing per era
  </p>
  <ul>
  {% for entry in summary %}
    {% if entry['samples']|length > 0 %}
      <li class="current">
        <span style="font-size: 1.2em">
          {{entry['era']}}
        </span> 
        ({{ entry['samples']|length }}) [<span onclick="javascript: toggleChildren('cat{{loop.index}}');" id="toggle">
          toggle
        </span>]
        <div id="cat{{loop.index}}" class="sub_cat_box">
          <ul> 
          {% for sample in entry['samples'] %}
            <li>
              <a href="#{{ sample }}">
                {{ sample }}
              </a>
            </li>
          {% endfor %}
          </ul> 
        </div>
      </li>
    {% endif %}
  {% endfor %}
  </ul>
</div>
"""


class SmartFormatter(argparse.HelpFormatter):
  def _split_lines(self, text, width):
    if text.startswith('R|'):
      return text[2:].splitlines()
    return argparse.HelpFormatter._split_lines(self, text, width)

def generate_toc(categories):
  return jinja2.Template(TOC_TEMPLATE).render(categories = categories)

def generate_summary(summary):
  return jinja2.Template(SUMMARY_TEMPLATE).render(summary = summary)

def generate_table(sample, important_eras):
  rows = []
  for era in sample['datasets']:
    is_important = era in important_eras
    rows.append(
      jinja2.Template(ROW_TEMPLATE).render(
        era = era,
        datasets = list(map(lambda x: (x['dbs'], 'fastsim' in x['alt'] if 'alt' in x else False), sample['datasets'][era])),
        is_important = is_important
      )
    )

  xs_value = sample['xs']['value']
  if xs_value > 1e6:
    xs_value = '%.3e' % sample['xs']['value']
  table = jinja2.Template(TABLE_TEMPLATE).render(
    sample_name = sample['name'],
    table_rows  = rows,
    xs          = xs_value,
    order       = sample['xs']['order'],
    refs        = sample['xs']['references'],
    comment     = sample['xs']['comment'],
  )

  return table

def generate_heading(category_name):
  return jinja2.Template(HEADING_TEMPLATE).render(category_name = category_name)

parser = argparse.ArgumentParser(
  formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
)
parser.add_argument(
  '-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
  help = 'R|Input JSON file containing datasets',
)
parser.add_argument(
  '-o', '--output', dest = 'output', metavar = 'file', required = False, type = str,
  help = 'R|Output HTML file',
)
parser.add_argument(
  '-d', '--directory', dest = 'directory', metavar = 'directory', required = False, type = str, default = '.',
  help = 'R|Output directory',
)
parser.add_argument(
  '-e', '--eras', dest = 'eras', metavar = 'eras', required = False, type = str, nargs = '+',
  choices = [
    'RunIISummer16MiniAODv2', 'RunIISummer16MiniAODv3', 'RunIIFall17MiniAOD', 'RunIIFall17MiniAODv2', 'RunIIAutumn18MiniAOD'
  ],
  default = [ 'RunIISummer16MiniAODv3', 'RunIIFall17MiniAODv2', 'RunIIAutumn18MiniAOD' ],
  help = 'R|Standout eras',
)
args = parser.parse_args()

input_filename = args.input
output_filename = args.output
output_dirname = os.path.abspath(os.path.expanduser(args.directory))
important_eras = args.eras

if not output_filename:
  output_filename = '%s.html' % os.path.splitext(os.path.basename(input_filename))[0]

if not os.path.isdir(output_dirname):
  raise ValueError('No such directory: %s' % args.directory)

output_filename = os.path.join(output_dirname, output_filename)

with open(input_filename, 'r') as f:
  json_data = json.load(f)

summary_arr = []

for important_era in important_eras:
  summary_arr.append({
    'era'     : important_era,
    'samples' : [],
  })

html_filled = ""
toc_arr = []

for i, cat in enumerate(json_data):
  toc_arr.append({
    'name'    : cat['category'],
    'samples' : [],
    'nof_ok'  : 0,
  })
  html_filled += generate_heading(cat['category'])
  samples = cat['samples']

  for sample in samples:
    is_ok = all(map(lambda era: len(sample['datasets'][era]) > 0, important_eras))

    for era in sample['datasets']:
      if era not in important_eras:
        continue
      if not sample['datasets'][era]:
        for entry in summary_arr:
          if entry['era'] == era:
            entry['samples'].append(sample['name'])
            break

    toc_arr[-1]['samples'].append({
      'name' : sample['name'],
      'is_ok' : is_ok,
    })
    toc_arr[-1]['nof_ok'] += int(is_ok)

    html_filled += generate_table(sample, important_eras)

toc_filled = generate_toc(toc_arr)
summary_filled = generate_summary(summary_arr)

with open(output_filename, 'w') as f:
  f.write(jinja2.Template(HTML_TEMPLATE).render(
    toc          = toc_filled,
    tables       = html_filled,
    current_time = str(datetime.datetime.now()),
    summary      = summary_filled,
  ))
