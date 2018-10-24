# Auto generated configuration file
# using:
# Revision: 1.19
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v
# with command line options:
# nanoAOD --step=NANO --era=Run2_2017,run2_nanoAOD_94XMiniAODv1 --no_exec --fileout=tree.root --number=-1 \
# --customise_commands=process.MessageLogger.cerr.FwkReport.reportEvery = 1000\n\
# process.source.fileNames = cms.untracked.vstring()\n\
# from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; \
# addJetSubstructureObservables(process)\n --data --eventcontent NANOAOD --datatier NANOAOD \
# --conditions 94X_dataRun2_v6 --python_filename=nano_cfg_data_2017.py \
# --lumiToProcess=Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt
import FWCore.ParameterSet.Config as cms

from Configuration.StandardSequences.Eras import eras

import FWCore.ParameterSet.Types as CfgTypes # custom
import FWCore.PythonUtilities.LumiList as LumiList # custom
import os # custom

# custom
JSONfile = os.path.join(
  os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'data',
  'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt'
)

process = cms.Process('NANO',eras.Run2_2017,eras.run2_nanoAOD_94XMiniAODv1)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:nanoAOD_PAT.root'),
    lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange( # custom
        LumiList.LumiList(filename = JSONfile).getCMSSWString().split(',')
    )),
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

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('tree.root'),
    outputCommands = process.NANOAODEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '94X_dataRun2_v6', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequence)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeData

#call to customisation function nanoAOD_customizeData imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeData(process)

# End of customisation functions

# Customisation from command line

process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.source.fileNames = cms.untracked.vstring()
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; addJetSubstructureObservables(process)
from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets; addLeptonSubtractedAK8Jets(process, False)

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
  processDumpFile = open('nano_data_2017.dump', 'w')
  print >> processDumpFile, process.dumpPython()
  processDumpFile.close()
