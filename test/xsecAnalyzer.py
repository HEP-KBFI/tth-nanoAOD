import FWCore.ParameterSet.Config as cms

inputFiles = [

]

process = cms.Process('XSEC')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic8TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from Configuration.AlCa.GlobalTag import GlobalTag

process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v13', '')
process.maxEvents = cms.untracked.PSet(
  input = cms.untracked.int32(-1),
)

process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.source = cms.Source(
  "PoolSource",
  fileNames          = cms.untracked.vstring(inputFiles),
  duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
)

process.genxsec = cms.EDAnalyzer("GenXSecAnalyzer")

process.p = cms.Path(process.genxsec)
process.schedule = cms.Schedule(process.p)
