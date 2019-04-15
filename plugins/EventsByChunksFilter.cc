#include "tthAnalysis/NanoAOD/plugins/EventsByChunksFilter.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include <iostream>

EventsByChunksFilter::EventsByChunksFilter(const edm::ParameterSet& cfg)
  : skipEvents_(cfg.getParameter<unsigned>("skipEvents"))
  , selectEvents_(cfg.getParameter<unsigned>("selectEvents"))
  , numEvents_processed_(0)
  , numEvents_selected_(0)
{}

EventsByChunksFilter::~EventsByChunksFilter()
{
  edm::LogInfo ("~EventsByChunksFilter") 
    << " #Events processed = " << numEvents_processed_ << std::endl
    << " #Events selected = " << numEvents_selected_ << " (skipEvents = " << skipEvents_ << ", selectEvents = " << selectEvents_ << ")" << std::endl;
}

bool EventsByChunksFilter::filter(edm::Event& evt, const edm::EventSetup& es)
{
  ++numEvents_processed_;
  if ( numEvents_processed_ > skipEvents_ && numEvents_selected_ < selectEvents_ ) {
    ++numEvents_selected_;
    return true;  // select event
  } else {
    return false; // reject event
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(EventsByChunksFilter);

