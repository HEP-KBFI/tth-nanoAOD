# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options:
# nanoAOD --step=NANO --era=Run2_2017,run2_nanoAOD_94XMiniAODv1 --no_exec --fileout=tree.root --number=-1 \
# --customise_commands=process.MessageLogger.cerr.FwkReport.reportEvery = 1000\n\
# process.source.fileNames = cms.untracked.vstring()\n\
# from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; \
# addJetSubstructureObservables(process, True)\n --mc --eventcontent NANOAODSIM --datatier NANOAODSIM \
# --conditions 94X_mc2017_realistic_v13 --python_filename=nano_cfg_mc_2017.py
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

process = cms.Process('NANO',eras.Run2_2017,eras.run2_nanoAOD_94XMiniAODv1)

# import of standard configurations
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

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:nanoAOD_PAT.root'),
#    eventsToProcess = cms.untracked.VEventRange(), # custom; format: run:lumi:event, one string per event
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(

)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('nanoAOD nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('tree.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '94X_mc2017_realistic_v13', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC

#call to customisation function nanoAOD_customizeMC imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeMC(process)

# End of customisation functions

# Customisation from command line

process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source.fileNames = cms.untracked.vstring()
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; addJetSubstructureObservables(process, True)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

# custom til the end; enable any of those only if you're debugging
if False:
  process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
    ignoreTotal         = cms.untracked.int32(1),
    oncePerEventMode    = cms.untracked.bool(True),
    moduleMemorySummary = cms.untracked.bool(True),
  )
if False:
  process.Tracer = cms.Service("Tracer",
    printTimestamps = cms.untracked.bool(True),
  )
if False:
  processDumpFile = open('nano_mc_2017.dump', 'w')
  print >> processDumpFile, process.dumpPython()
  processDumpFile.close()
