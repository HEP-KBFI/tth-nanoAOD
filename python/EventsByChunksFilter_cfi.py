import FWCore.ParameterSet.Config as cms

# The following configuration selects the first 50000 events.
# Set skipEvents to 50000 for to select the second "chunk" of events.
# Reduce the value of selectEvents to split the event processing into more chunks.
eventsByChunksFilter = cms.EDFilter("EventsByChunksFilter",
    skipEvents = cms.uint32(0),
    selectEvents = cms.uint32(50000)                                 
)
