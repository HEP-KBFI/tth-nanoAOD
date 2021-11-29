#!/usr/bin/env python

# Script for dumpting LHE headers and weights

from tthAnalysis.HiggsToTauTau.safe_root import ROOT # force batch mode

import DataFormats.FWLite # Events, Handle, Runs

import os.path
import argparse
import textwrap
import logging
import sys

DESCRIPTION = r"""In case you want to open remote files,
make sure that you've opened your proxy:

  voms-proxy-init -voms cms -valid 24:00
"""

XDR_SCHEMA = 'root://cms-xrd-global.cern.ch/'
CMS_STORE = '/hdfs/cms'
FILE_SCHEMA = 'file://'
LHE_HANDLES = [ 'source', 'externalLHEProducer' ]  # 'source' was the label in some older samples

# https://stackoverflow.com/a/64102901/4056193
class RawFormatter(argparse.HelpFormatter):
  def _fill_text(self, text, width, indent):
    return '\n'.join([ textwrap.fill(line, width) for line in textwrap.dedent(text).splitlines() ])

def get_rle(event):
  aux = event.eventAuxiliary()
  run_nr = aux.run()
  lumi_nr = aux.luminosityBlock()
  evt_nr = aux.event()
  del aux
  return '{}:{}:{}'.format(run_nr, lumi_nr, evt_nr)

def find_event(event_handle, evt_nr):
  nof_events = event_handle.size()
  retval = 0 # just pick the first event

  if nof_events <= 0:
    logging.debug("No events found in the file -> exiting")
    retval = -1
  elif evt_nr:
    evt_found = False
    for i in range(nof_events):
      event_handle.to(i)
      rle = get_rle(event_handle)
      evt_str = rle.split(':')[-1]
      if evt_str == evt_nr:
        evt_found = True
        break
    if not evt_found:
      logging.error(
        "No such event number found in file {}: {}".format(', '.join(event_handle._filenames), evt_found))
      retval = -1

  return retval

def check_generator(event_handle):
  genhandle = DataFormats.FWLite.Handle('GenEventInfoProduct')
  has_generator = event_handle.getByLabel('generator', genhandle)
  if has_generator:
    genprod = genhandle.product()
    alpha_qed = genprod.alphaQED()
    alpha_qcd = genprod.alphaQCD()
    qScale = genprod.qScale()
    gen_weight = genprod.weight()

    logging.debug(
      "alphaQED = {:.9f} alphaQCD = {:.9f} qScale = {:.9f} genWeight = {:.9f}".format(
        alpha_qed, alpha_qcd, qScale, gen_weight,
      )
    )
    if genprod.hasPDF():
      pdf = genprod.pdf()
      logging.debug(
        "x1 = {:.9f} x2 = {:.9f} id1 = {} id2 = {} xpdf1 = {:.9f} xpdf2 = {:.9f}".format(
          pdf.x.first, pdf.x.second, pdf.id.first, pdf.id.second, pdf.xPDF.first, pdf.xPDF.second,
        )
      )
      del pdf
  else:
    logging.error("{} object not found in file {}".format(genhandle._type, ', '.join(event_handle._filenames)))

  del genhandle
  return has_generator

def dump_lhe_weights(event_handle):
  lhehandle = DataFormats.FWLite.Handle('LHEEventProduct')
  has_lhe = False
  for lhehandle_label in LHE_HANDLES:
    if has_lhe:
      break
    has_lhe = event_handle.getByLabel(lhehandle_label, lhehandle)

  weights_parsed = []
  if has_lhe:

    lheprod = lhehandle.product()
    # LHE particles accessible via lheprod.hepeup(), cf SimDataFormats/GeneratorProducts/interface/LesHouches.h
    lhe_nomweight = lheprod.originalXWGTUP()
    weights = lheprod.weights()
    logging.debug('originalXWGTUP = {:.9f} #weights = {}'.format(lhe_nomweight, weights.size()))

    for weight in weights:
      weights_parsed.append('{:>8} {:.9f} {:.9f}'.format(weight.id, weight.wgt, weight.wgt / lhe_nomweight))

    del lheprod
  else:
    logging.error("{} object not found in file {}".format(lhehandle._type, ', '.join(event_handle._filenames)))


  del lhehandle
  return weights_parsed

def dump_lhe_header(input_filename):
  run_handle = DataFormats.FWLite.Runs(input_filename)
  lherunhandle = DataFormats.FWLite.Handle('LHERunInfoProduct')
  has_lhe = False
  for lhehandle_label in LHE_HANDLES:
    if has_lhe:
      break
    has_lhe = run_handle.getByLabel(lhehandle_label, lherunhandle)

  lhe_headers = []
  if has_lhe:
    lheprod = lherunhandle.product()

    # see SimDataFormats/GeneratorProducts/interface/LesHouches.h
    # https://arxiv.org/abs/hep-ph/0109068
    heprup = lheprod.heprup()
    # LHA ID of the 1st and 2nd beam hadron
    pdf_lhaid1 = heprup.PDFSUP.first
    pdf_lhaid2 = heprup.PDFSUP.second
    # beam energy
    beam1 = heprup.EBMUP.first
    beam2 = heprup.EBMUP.second
    # beam hadrons
    pid1 = heprup.IDBMUP.first
    pid2 = heprup.IDBMUP.second
    # subprocesses ??
    nsub = heprup.NPRUP
    xsecs = [ heprup.XSECUP.at(i) for i in range(nsub) ]
    xsec_errs = [ heprup.XERRUP.at(i) for i in range(nsub) ]
    logging.debug("Beam 1: ID = {} PDF = {} energy = {:.2f} GeV".format(pid1, pdf_lhaid1, beam1))
    logging.debug("Beam 2: ID = {} PDF = {} energy = {:.2f} GeV".format(pid2, pdf_lhaid2, beam2))
    logging.debug(
      "{} subprocesses: {}".format(
        nsub, ", ".join([ "{:.3e} (+/- {:.3e})".format(xsecs[i], xsec_errs[i]) for i in range(nsub) ])
      )
    )
    del heprup

    nof_headers = lheprod.headers_size()
    nof_comments = lheprod.comments_size()

    if nof_headers > 0:
      it = lheprod.headers_begin()
      while it != lheprod.headers_end():
        lines = it.lines()
        tag = it.tag()
        nof_lines = lines.size()
        content = ''.join([ lines.at(i) for i in range(nof_lines) ])
        lhe_headers.append({ 'tag': tag, 'content' : content })
        it.next()
    logging.debug(
      "Found {} LHE headers: {}".format(
        nof_headers, ', '.join([ "'{}'".format(header['tag']) for header in lhe_headers ])
      )
    )

    logging.debug("Found {} comments".format(nof_comments))
    if nof_comments > 0:
      it = lheprod.comments_begin()
      comment_idx = 0
      while it != lheprod.comments_end():
        lines = it.lines()
        tag = it.tag()
        nof_lines = lines.size()
        comment = ''.join([ lines.at(i) for i in range(nof_lines) ])
        logging.debug("#{} comment ({}): {}".format(comment_idx, tag, comment))
        it.next()
        comment_idx += 1

  else:
    logging.error("{} object not found in file {}".format(lherunhandle._type, input_filename))

  del lherunhandle
  del run_handle
  return lhe_headers

def sanitize_input(input_filename):
  if input_filename.startswith('/store'):
    # first checking if the file exists in our tier
    input_local = CMS_STORE + input_filename
    if os.path.isfile(input_local):
      logging.debug("File {} exists locally".format(input_filename))
      input_filename = input_local
    else:
      logging.debug("File name starts with /store -> will prefix xdr schema")
      input_filename = XDR_SCHEMA + input_filename
  if not input_filename.startswith(XDR_SCHEMA) and not input_filename.startswith(FILE_SCHEMA):
    input_filename = FILE_SCHEMA + input_filename
  logging.debug('Processing: {}'.format(input_filename))
  return input_filename

def process(input_filename, evt_str, dump_header, print_weights, output_dir):
  if dump_header:
    headers = dump_lhe_header(input_filename)
    if output_dir:
      for idx, header in enumerate(headers):
        output_fn = 'header.{}'.format(idx)
        if header['tag']:
          output_fn += '.{}'.format(header['tag'].replace(' ', '-'))
        output_fn += '.txt'
        output_path = os.path.join(output_dir, output_fn)
        with open(output_path, 'w') as output_f:
          output_f.write(header['content'])
        logging.debug('Wrote file: {}'.format(output_path))
    else:
      for header in headers:
        print('Header: {}'.format(header['tag']))
        print(''.join(header['content']))
        print('=' * 150)

  if print_weights:
    event_handle = DataFormats.FWLite.Events(input_filename)
    evt_nr = find_event(event_handle, evt_str)
    if evt_nr >= 0:
      event_handle.to(evt_nr)
      rle = get_rle(event_handle)
      logging.debug("Parsing event {}".format(rle))

      check_generator(event_handle)
      weights_parsed = dump_lhe_weights(event_handle)
      print('\n'.join(weights_parsed))

    del event_handle

  return

def parse_args():
  parser = argparse.ArgumentParser(description = DESCRIPTION, formatter_class = RawFormatter)
  parser.add_argument('-i', '--input', dest = 'input', metavar = 'name', required = True, type = str,
                      help = 'Input file name')
  parser.add_argument('-o', '--output', dest = 'output', metavar = 'directory', required = False, type = str, default = '',
                      help = 'Output directory')
  parser.add_argument('-e', '--event', dest = 'event', metavar = 'nr', required = False, type = int, default = -1,
                      help = 'Event number')
  parser.add_argument('-d', '--dump-header', dest = 'dump_header', action = 'store_true', default = False,
                      help = 'Dump header')
  parser.add_argument('-w', '--print-weights', dest = 'print_weights', action = 'store_true', default = False,
                      help = 'Print weights')
  parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
                      help = 'Verbose output')
  args = parser.parse_args()

  return args

if __name__ == '__main__':
  args = parse_args()
  
  logging.basicConfig(
    stream = sys.stdout,
    level  = logging.DEBUG if args.verbose else logging.INFO,
    format = '%(asctime)s - %(levelname)s: %(message)s',
  )

  input_filename = sanitize_input(args.input)
  evt_str = str(args.event) if args.event >= 0 else ''
  output_dir = os.path.abspath(args.output) if args.output else ''
  if output_dir and not os.path.isdir(output_dir):
    raise RuntimeError("No such directory: ")
  process(input_filename, evt_str, args.dump_header, args.print_weights, output_dir)
