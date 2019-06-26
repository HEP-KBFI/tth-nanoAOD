#!/usr/bin/env python

import sys
import json

intxt = sys.stdin.read()
json_data = json.loads(intxt)

nan_str = 'nan'
errors = {}
for jobId in json_data:
  entry = json_data[jobId]
  if entry['State'] == 'failed':
    if 'Error' not in entry:
      if nan_str not in errors:
        errors[nan_str] = []
      errors[nan_str].append(jobId)
      continue
    error_code = entry['Error'][0]
    if error_code not in errors:
      errors[error_code] = []
    errors[error_code].append(jobId)

for error_code in errors:
  print('{} {}'.format(error_code, ','.join(errors[error_code])))

