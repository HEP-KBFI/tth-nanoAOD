#ifndef tthAnalysis_NanoAOD_EventsByChunksFilter_h
#define tthAnalysis_NanoAOD_EventsByChunksFilter_h

/** \class EventsByChunksFilter
 *
 * Select a set of N events, starting at event K + 1. 
 * The functionality of this class is to process large input files in "chunks",
 * which is useful in case the input files contain too many (> 50000) events.
 * The configutation parameters 'selectEvents' and 'skipEvents' specify the values of N and K, respectively.
 * 
 * \author Christian Veelken, Tallinn
 *
 */

#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

class EventsByChunksFilter : public edm::EDFilter
{
 public:
  // constructor 
  explicit EventsByChunksFilter(const edm::ParameterSet&);
    
  // destructor
  virtual ~EventsByChunksFilter();
    
 private:
  bool filter(edm::Event&, const edm::EventSetup&);

  long skipEvents_;
  long selectEvents_;

  long numEvents_processed_;
  long numEvents_selected_;
};

#endif   
