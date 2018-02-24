import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC, nanoAOD_customizeData # custom
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables # custom

import FWCore.ParameterSet.Types as CfgTypes # custom
import FWCore.PythonUtilities.LumiList as LumiList # custom

import os

JSONfile = os.path.join(
  os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'data',
  'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
)

process = cms.Process('NANO', eras.Run2_2017)

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.load("Configuration.StandardSequences.GeometryDB_cff")

process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(-1),
)

process.options = cms.untracked.PSet(
  wantSummary = cms.untracked.bool(True),
)

process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(
    #
  ),
)

# custom until end
process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
  calibratedPatElectrons = cms.PSet(
    initialSeed = cms.untracked.uint32(81),
    engineName  = cms.untracked.string('TRandom3'),
  ),
  calibratedPatPhotons = cms.PSet(
    initialSeed = cms.untracked.uint32(81),
    engineName  = cms.untracked.string('TRandom3'),
  ),
)


process.nanoPath            = cms.Path(process.nanoSequence)
process                     = nanoAOD_customizeData(process)
process.GlobalTag.globaltag = '94X_dataRun2_ReReco_EOY17_v2'

process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
lumisToProcess = LumiList.LumiList(filename = JSONfile).getCMSSWString().split(',')
process.source.lumisToProcess.extend(lumisToProcess)

#--------------------------------------------------------------------------------
# CV: customization with jet substructure observables for hadronic top reconstruction (boosted and non-boosted)
addJetSubstructureObservables(process, False)
#--------------------------------------------------------------------------------

process.out = cms.OutputModule("NanoAODOutputModule",
  fileName             = cms.untracked.string('tree.root'),
  outputCommands       = process.NanoAODEDMEventContent.outputCommands,
#  compressionLevel     = cms.untracked.int32(9),
#  compressionAlgorithm = cms.untracked.string("LZMA"),
)

#--------------------------------------------------------------------------------
if False: # set True when debugging
  process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
    ignoreTotal         = cms.untracked.int32(1),
    oncePerEventMode    = cms.untracked.bool(True),
    moduleMemorySummary = cms.untracked.bool(True),
  )
  process.Tracer = cms.Service("Tracer",
    printTimestamps = cms.untracked.bool(True),
  )
#--------------------------------------------------------------------------------

process.end = cms.EndPath(process.out)

#--------------------------------------------------------------------------------
# CV: dump python config
#processDumpFile = open('nano.dump', 'w')
#print >> processDumpFile, process.dumpPython()
#processDumpFile.close()
#--------------------------------------------------------------------------------
