import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
process = cms.Process('NANO',eras.Run2_2017,eras.run2_nanoAOD_92X)

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.StandardSequences.Services_cff')
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = autoCond['phase1_2017_realistic']

process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.MessageLogger.cerr.FwkReport.reportEvery = 100
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(10000))

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
process.source.fileNames = [
#relvals:
# '/store/relval/CMSSW_9_3_0_pre4/RelValTTbar_13/MINIAODSIM/93X_mc2017_realistic_v1-v1/00000/1CFF7C9C-6A86-E711-A1F2-0CC47A7C35F4.root',
# '/store/relval/CMSSW_9_3_0_pre4/RelValTTbar_13/MINIAODSIM/93X_mc2017_realistic_v1-v1/00000/107D499F-6A86-E711-8A51-0025905B8592.root',

#sample with LHE
#	'/store/mc/RunIISummer17MiniAOD/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/MINIAODSIM/92X_upgrade2017_realistic_v10_ext1-v1/110000/187F7EDA-0986-E711-ABB3-02163E014C21.root'
    'file:/hdfs/cms/store/mc/RunIISummer17MiniAOD/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/92X_upgrade2017_realistic_Candidate_forECALStudies_ext1-v1/70000/FC9F9AAD-29A4-E711-8FCD-0CC47A4D7670.root'
]

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
process.end = cms.EndPath(process.out+process.out1)  

#--------------------------------------------------------------------------------
# CV: dump python config
processDumpFile = open('nano.dump', 'w')
print >> processDumpFile, process.dumpPython()
#--------------------------------------------------------------------------------
