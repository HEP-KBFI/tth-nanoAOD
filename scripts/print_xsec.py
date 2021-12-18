#!/usr/bin/env cmsRun

import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

import os.path

options = VarParsing()
options.register(
  name    = 'inputRootFiles',
  default = [],
  mult    = VarParsing.multiplicity.list,
  mytype  = VarParsing.varType.string,
  info    = "Input ROOT files",
)
options.register(
  name    = 'inputTextFile',
  default = '',
  mult    = VarParsing.multiplicity.singleton,
  mytype  = VarParsing.varType.string,
  info    = "Input file containing list of ROOT files",
)
options.register(
  name    = 'maxEvents',
  default = -1,
  mult    = VarParsing.multiplicity.singleton,
  mytype  = VarParsing.varType.int,
  info    = "Maximum number of events to consider",
)
options.register(
  name    = 'logEvery',
  default = 10000,
  mult    = VarParsing.multiplicity.singleton,
  mytype  = VarParsing.varType.int,
  info    = "Logging interval",
)
options.parseArguments()

# one or the other but not both
assert(bool(options.inputRootFiles) != bool(options.inputTextFile))

inputFiles = []
if options.inputTextFile:
  assert(os.path.isfile(options.inputTextFile))
  with open(options.inputTextFile, 'r') as inputTextFile:
    for line in inputTextFile:
      inputFiles.append(line.strip())
else:
  inputFiles = options.inputRootFiles

inputFilesPrepended = []
for inputFile in inputFiles:
  if inputFile.startswith('/store'):
    inputFileLocal = '/hdfs/cms{}'.format(inputFile)
    if os.path.isfile(inputFileLocal):
      inputFilesPrepended.append(inputFileLocal)
    else:
      inputFilesPrepended.append('root://cms-xrd-global.cern.ch/{}'.format(inputFile))
  elif os.path.isfile(inputFile):
    inputFilesPrepended.append('file://{}'.format(inputFile))
  else:
    inputFilesPrepended.append(inputFile)

print("Found {} file(s)".format(len(inputFilesPrepended)))

process = cms.Process('XSEC')

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = options.logEvery

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(options.maxEvents),
)
process.source = cms.Source(
  "PoolSource",
  fileNames          = cms.untracked.vstring(inputFilesPrepended),
  duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

process.genxsec = cms.EDAnalyzer("GenXSecAnalyzer")

process.p = cms.Path(process.genxsec)
process.schedule = cms.Schedule(process.p)
