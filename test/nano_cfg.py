import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.Types as CfgTypes
import FWCore.PythonUtilities.LumiList as LumiList

from Configuration.StandardSequences.Eras import eras
from Configuration.AlCa.autoCond import autoCond
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC, nanoAOD_customizeData

from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables

import os

isDEBUG         = False
#isMC            = True
isMC            = False
global_tag_data = '94X_dataRun2_ReReco_EOY17_v2'
global_tag_mc   = '94X_mc2017_realistic_v10'
JSONfile = os.path.join(
  os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'data', 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
)

process = cms.Process('NANO', eras.Run2_2017)

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("RecoBTag.Configuration.RecoBTag_cff")
process.load("PhysicsTools.NanoAOD.nano_cff")

process.options   = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring()
)

#--------------------------------------------------------------------------------
# only for testing !!
#process.source.fileNames = cms.untracked.vstring(
#  'file:/home/ram/VHBB_NTUPLES_2017/NANO_AOD_DEV/CMSSW_9_4_4_Feb19_2018_Latest_After_boosted_code_bugfix/src/tthAnalysis/NanoAOD/test/CE96B3D0-90FB-E711-9DB4-002590A80E1E.root'
#)
#process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))
#--------------------------------------------------------------------------------

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

if isMC:
  process.nanoPath = cms.Path(process.nanoSequenceMC)
  process          = nanoAOD_customizeMC(process)
  process.GlobalTag.globaltag = global_tag_mc
else:
  process.nanoPath = cms.Path(process.nanoSequence)
  process          = nanoAOD_customizeData(process)
  process.GlobalTag.globaltag = global_tag_data

  process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
  lumisToProcess = LumiList.LumiList(filename = JSONfile).getCMSSWString().split(',')
  process.source.lumisToProcess.extend(lumisToProcess)

#--------------------------------------------------------------------------------
# CV: customization with jet substructure observables for hadronic top reconstruction (boosted and non-boosted)
addJetSubstructureObservables(process, isMC)
#--------------------------------------------------------------------------------

process.out = cms.OutputModule("NanoAODOutputModule",
    fileName       = cms.untracked.string('tree.root'),
    outputCommands = process.NanoAODEDMEventContent.outputCommands,
    #compressionLevel     = cms.untracked.int32(9),
    #compressionAlgorithm = cms.untracked.string("LZMA"),
)

#--------------------------------------------------------------------------------
if isDEBUG:
  process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
      ignoreTotal         = cms.untracked.int32(1),
      oncePerEventMode    = cms.untracked.bool(True),
      moduleMemorySummary = cms.untracked.bool(True),
  )
  process.Tracer = cms.Service("Tracer",
      printTimestamps = cms.untracked.bool(True),
  )
  if hasattr(process,'options'):
      process.options.wantSummary = cms.untracked.bool(True)
  else:
      process.options = cms.untracked.PSet(
          wantSummary = cms.untracked.bool(True),
      )
#--------------------------------------------------------------------------------

process.end = cms.EndPath(process.out)

#--------------------------------------------------------------------------------
# CV: dump python config
#processDumpFile = open('nano.dump', 'w')
#print >> processDumpFile, process.dumpPython()
#--------------------------------------------------------------------------------
