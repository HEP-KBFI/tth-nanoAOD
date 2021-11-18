#!/usr/bin/env python

# Preparations:
# 1) open proxy for DAS queries:
#    source /cvmfs/cms.cern.ch/common/crab-setup.sh
#    voms-proxy-init -voms cms -valid 24:00
# 2) get your cookie for about 10 hours, needed by McM queries:
#    cern-get-sso-cookie --cert ~/.globus/usercert.pem    \
#                        --key ~/.globus/userkey.pem      \
#                        -u https://cms-pdmv.cern.ch/mcm/ \
#                        -o cookie.txt

import sys
import argparse
import os
import logging
import time
import textwrap
import json
import pycurl
import io

# DAS
import dbs.apis.dbsClient as dbsClient

DESCRIPTION=r"""Before running, make sure that you've opened your proxy:

  source /cvmfs/cms.cern.ch/common/crab-setup.sh
  voms-proxy-init -voms cms -valid 24:00

and obtained cookie with:

  cern-get-sso-cookie --cert ~/.globus/usercert.pem    \
                      --key  ~/.globus/userkey.pem     \
                      -u https://cms-pdmv.cern.ch/mcm/ \
                      -o cookie.txt
"""

QUERIES = [ 'generator', 'fragment' ]

# https://stackoverflow.com/a/64102901/4056193
class RawFormatter(argparse.HelpFormatter):
  def _fill_text(self, text, width, indent):
    return '\n'.join([ textwrap.fill(line, width) for line in textwrap.dedent(text).splitlines() ])

# dumbed-down version of the origina McM class (/afs/cern.ch/cms/PPD/PdmV/tools/McM/)
class McM:
  def __init__(self, cookie):
    self.host = 'cms-pdmv.cern.ch'
    self.cookie = cookie
    self.server = 'https://{}/mcm/'.format(self.host)
    self.max_retries = 3

    if not os.path.isfile(self.cookie):
      raise RuntimeError('Cookie not found: %s' % self.cookie)

  def __get(self, url, data = None):
    query = self.server + url
    buf = io.BytesIO()
    nof_retries = 0
    while nof_retries < self.max_retries:
      c = pycurl.Curl()
      c.setopt(pycurl.COOKIEJAR, self.cookie)
      c.setopt(pycurl.COOKIEFILE, self.cookie)
      c.setopt(c.URL, query)
      c.setopt(c.WRITEDATA, buf)
      try:
        c.perform()
        assert(c.getinfo(pycurl.RESPONSE_CODE) == 200)
        c.close()
        break
      except BaseException as e:
        nof_retries += 1
        time.sleep(nof_retries**2)
    body = buf.getvalue().decode('utf-8')
    return json.loads(body) if body else None

  def get(self, object_type, object_id = None, query = '', page = -1):
    if object_id: # prep id
      object_id = object_id.strip()
      url = '/'.join([ 'restapi', object_type, 'get', object_id ])
      result = self.__get(url).get('results')
      if not result:
        return None
      return result
    elif query: # tag-based, eg tags=M17p1A&pwg=HIG
      if page != -1: # specific page requested
        url_parts = {
          'db_name' : object_type,
          'limit'   : 50,
          'page'    : page,
        }
        url_encoded = '&'.join([ '{}={}'.format(*kv) for kv in url_parts.items() ] + [ query ])
        url = 'search/?{}'.format(url_encoded)
        results = self.__get(url).get('results', [])
        return results
      else: # request all pages
        page_results = [{}]
        results = []
        page = 0
        while page_results:
          page_results = self.get(object_type = object_type, query = query, page = page)
          results += page_results
          page += 1
        return results
    else:
      logging.error('Neither object ID, nor query is given, doing nothing ...')

def parse_args():
  parser = argparse.ArgumentParser(description = DESCRIPTION, formatter_class = RawFormatter)
  parser.add_argument('-i', '--input', dest = 'input', metavar = 'name', required = True, type = str,
                      help = 'DBS name')
  parser.add_argument('-q', '--query', dest = 'query', metavar = 'type', required = True, type = str, choices = QUERIES,
                      help = 'Requested query')
  parser.add_argument('-c', '--cookie', dest = 'cookie', metavar = 'path', required = False, type = str, default = 'cookie.txt',
                      help = 'SSO cookie')
  parser.add_argument('-o', '--output', dest = 'output', metavar = 'output', required = False, type = str, default = '',
                      help = 'Output file (only if no -n or -u supplied)')
  parser.add_argument('-d', '--debug', dest = 'debug', action = 'store_true', default = False,
                      help = 'Verbose output')
  parser.add_argument('-n', '--notes', dest = 'notes', action = 'store_true', default = False,
                      help = 'Print notes if fragment missing')
  parser.add_argument('-u', '--url', dest = 'url', action = 'store_true', default = False,
                      help = 'Return URL instead')
  parser.add_argument('-s', '--silent', dest = 'silent', action = 'store_true', default = False,
                      help = 'Silent mode')
  args = parser.parse_args()

  return args

def get_prep_id(dataset):
  dbs = dbsClient.DbsApi('https://cmsweb.cern.ch/dbs/prod/global/DBSReader')
  dbs_response = dbs.listDatasetArray(dataset = dataset, detail = True)
  if not dbs_response:
    raise RuntimeError("Invalid dataset: %s" % dataset)
  prep_id = dbs_response[0]['prep_id']
  logging.debug('Got prep ID: {}'.format(prep_id))
  return prep_id

def get_campaign_data(mcm, prep_id):
  return mcm.get('requests', prep_id)

def get_fragment(mcm, campaign_data, print_notes = False, return_url = False):
  join_chain = [ history for history in campaign_data['history'] if history['action'] == 'join chain' ]
  assert(join_chain)
  first_ancestor = join_chain[0]['step'] # first one in history
  logging.debug('Got chain ID: {}'.format(first_ancestor))

  chain_data = mcm.get('chained_requests', first_ancestor)
  ancestor_id = chain_data['chain'][0]
  logging.debug('Got ancestor ID: {}'.format(ancestor_id))

  ancestor_data = get_campaign_data(mcm, ancestor_id)
  fragment = ancestor_data['fragment']

  if return_url:
    return 'https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_fragment/{}'.format(ancestor_id)

  if not fragment and print_notes:
    logging.debug('No fragment found, returning notes instead') # may contain a link to original cards
    fragment = ancestor_data['notes']
  return fragment

if __name__ == '__main__':
  args = parse_args()

  logging.basicConfig(
    stream = sys.stdout,
    level  = logging.DEBUG if (args.debug and not args.silent) else logging.INFO,
    format = '%(asctime)s - %(levelname)s: %(message)s',
  )

  prep_id = get_prep_id(args.input)

  mcm = McM(cookie = args.cookie)
  campaign_data = get_campaign_data(mcm, prep_id)

  if args.query == 'generator':
    generators = [ generator for generator in campaign_data['generators'] if generator ]
    print(', '.join(generators))
  elif args.query == 'fragment':
    fragment = get_fragment(mcm, campaign_data, args.notes, args.url)
    if not args.silent:
      print(fragment)
    if args.output and not (args.notes or args.url):
      output_dir = os.path.dirname(os.path.abspath(args.output))
      if not os.path.isdir(output_dir):
        raise RuntimeError("No such directory: %s" % output_dir)
      with open(args.output, 'w') as output:
        output.write(fragment)
  else:
    assert(False)
