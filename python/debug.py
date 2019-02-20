import FWCore.ParameterSet.Config as cms

def debug(process, dump = False, dumpFile = 'nano.dump', tracer = False, memcheck = False):
  if memcheck:
    process.SimpleMemoryCheck = cms.Service("SimpleMemoryCheck",
      ignoreTotal         = cms.untracked.int32(1),
      oncePerEventMode    = cms.untracked.bool(True),
      moduleMemorySummary = cms.untracked.bool(True),
    )
  if tracer:
    process.Tracer = cms.Service("Tracer",
      printTimestamps = cms.untracked.bool(True),
    )
  if dump:
    processDumpFile = open(dumpFile, 'w')
    print >> processDumpFile, process.dumpPython()
    processDumpFile.close()