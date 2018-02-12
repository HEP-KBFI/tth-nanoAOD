import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process('NANO',eras.Run2_2017)

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")
process.load("RecoBTag.Configuration.RecoBTag_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = autoCond['phase1_2017_realistic']

process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(300))

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
process.source.fileNames = [
  'file:///hdfs/local/karl/store/mc/RunIIFall17MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v1/00000/005DC030-D3F4-E711-889A-02163E01A62D.root'
]

enableDiagnostics = False
runOnMC = True
#runOnMC = False

process.load("PhysicsTools.NanoAOD.nano_cff")

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    calibratedPatElectrons = cms.PSet(
        initialSeed = cms.untracked.uint32(81),
        engineName = cms.untracked.string('TRandom3'),
    ),
    calibratedPatPhotons = cms.PSet(
        initialSeed = cms.untracked.uint32(81),
        engineName = cms.untracked.string('TRandom3'),
    ),
)
if runOnMC:
  process.nanoPath = cms.Path(process.nanoSequenceMC)
  process.calibratedPatElectrons.isMC = cms.bool(True)
  process.calibratedPatPhotons.isMC = cms.bool(True)
else:
  process.nanoPath = cms.Path(process.nanoSequence)
  process.GlobalTag.globaltag = autoCond['run2_data']

#--------------------------------------------------------------------------------
# CV: customization with jet substructure observables for hadronic top reconstruction (boosted and non-boosted)
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables
addJetSubstructureObservables(process, runOnMC)
#--------------------------------------------------------------------------------

process.out = cms.OutputModule("NanoAODOutputModule",
    fileName = cms.untracked.string('nano.root'),
    outputCommands = process.NanoAODEDMEventContent.outputCommands,
    #compressionLevel = cms.untracked.int32(9),
    #compressionAlgorithm = cms.untracked.string("LZMA"),
)
process.out1 = cms.OutputModule("NanoAODOutputModule",
    fileName = cms.untracked.string('lzma.root'),
    outputCommands = process.NanoAODEDMEventContent.outputCommands,
    compressionLevel = cms.untracked.int32(9),
    compressionAlgorithm = cms.untracked.string("LZMA"),
)

if enableDiagnostics:
    process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
      ignoreTotal         = cms.untracked.int32(1),
      oncePerEventMode    = cms.untracked.bool(True),
      moduleMemorySummary = cms.untracked.bool(True),
    )

    process.Tracer = cms.Service("Tracer",
        printTimestamps=cms.untracked.bool(True),
    )

    if hasattr(process,'options'):
        process.options.wantSummary = cms.untracked.bool(True)
    else:
        process.options = cms.untracked.PSet(
            wantSummary = cms.untracked.bool(True),
        )

process.end = cms.EndPath(process.out+process.out1)

#--------------------------------------------------------------------------------
# CV: dump python config
processDumpFile = open('nano.dump', 'w')
print >> processDumpFile, process.dumpPython()
#--------------------------------------------------------------------------------
