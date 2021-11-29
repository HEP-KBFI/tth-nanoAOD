#!/usr/bin/env cmsRun

# Example:
# genpart_printer.py inputFiles=firstFile.root,secondFile.root,thirdFile.root eventsToProcess=1:23:456,2:34:567
# genpart_printer.py inputFiles=oneFile.root maxEvents=4

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import os.path

XDR_SCHEMA = 'root://cms-xrd-global.cern.ch/'
CMS_STORE = '/hdfs/cms'
FILE_SCHEMA = 'file://'

def prepend(inputFiles):
  results = []
  for inputFile in inputFiles:
    prependedInput = inputFile
    if prependedInput.startswith('/store'):
      prependedInput_local = CMS_STORE + prependedInput
      if os.path.isfile(prependedInput_local):
        prependedInput = prependedInput_local
      else:
        prependedInput = XDR_SCHEMA + prependedInput
    if not prependedInput.startswith(XDR_SCHEMA) and not prependedInput.startswith(FILE_SCHEMA):
      prependedInput = FILE_SCHEMA + prependedInput
    results.append(prependedInput)
  return results

options = VarParsing('analysis')
options.register(
  name    = 'eventsToProcess',
  default = '',
  mult    = VarParsing.multiplicity.list,
  mytype  = VarParsing.varType.string,
  info    = "Events to process",
)
options.parseArguments()
inputFiles = prepend(options.inputFiles)
if not inputFiles:
  raise RuntimeError("No input files given")
max_to_print = max(options.maxEvents, len(options.eventsToProcess) if options.eventsToProcess else -1)
if max_to_print < 0:
  raise RuntimeError("Attempting to dump the gen particle listing of ALL events")

process = cms.Process('printGenParticles')

process.load('FWCore/MessageService/MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(options.maxEvents) # use -1 if you want to run over all events
)
process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(inputFiles),
)
if options.eventsToProcess:
  process.source.eventsToProcess = cms.untracked.VEventRange(options.eventsToProcess)

process.load('Configuration/StandardSequences/Services_cff')
process.s = cms.Sequence()

process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi',)
process.printGenParticleList = cms.EDAnalyzer('ParticleListDrawer',
  src = cms.InputTag('prunedGenParticles'),
  maxEventsToPrint = cms.untracked.int32(max_to_print),
)

process.s += process.printGenParticleList
process.p = cms.Path(process.s)
