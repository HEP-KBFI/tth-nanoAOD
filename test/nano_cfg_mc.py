import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC, nanoAOD_customizeData # custom
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables # custom

process = cms.Process('NANO', eras.Run2_2017) # [*]

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
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

process.nanoPath            = cms.Path(process.nanoSequenceMC)
process                     = nanoAOD_customizeMC(process)
process.GlobalTag.globaltag = '94X_mc2017_realistic_v13' # [**]

# [*] https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD#2017_MC_re_miniAOD_94X_version_2
# [**] is not recommended according to [**], but in practice the only difference b/w v13 and v14
#      is the JEC GT:
#          same as 94X_mc2017_realistic_v13 with update of JECs
#      (according to https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/94X_mc2017_realistic_v14)
#      The v14 GT uses Fall17_17Nov2017_V8_MC JECs, while v13 uses Fall17_17Nov2017_V6_MC
#      At the time of writing there is no data GT supporting Fall17_17Nov2017_V8_DATA JECs, and
#      since we want to avoid mixing different JEC versions, we decided to use v13 GT for MC.

#--------------------------------------------------------------------------------
# CV: customization with jet substructure observables for hadronic top reconstruction (boosted and non-boosted)
addJetSubstructureObservables(process, True)
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
