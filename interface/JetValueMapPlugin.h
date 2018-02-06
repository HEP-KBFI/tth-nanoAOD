#ifndef tthAnalysis_NanoAOD_JetValueMapPlugin_h
#define tthAnalysis_NanoAOD_JetValueMapPlugin_h

/** \class JetValueMapPlugin
 *
 * Add observables that have been computed externally and are stored in an edm::ValueMap
 * to pat::Jet object
 *
 * \author Christian Veelken, Tallinn
 *
 */

#include "tthAnalysis/NanoAOD/interface/JetExtendedPluginBase.h"

class JetValueMapPlugin : public JetExtendedPluginBase
{
 public:
  JetValueMapPlugin(const edm::ParameterSet& cfg);
  ~JetValueMapPlugin();
  
  virtual void operator()(pat::Jet& outputJet) const { assert(0); } // CV: force second operator() implementation with pat::Jet& and const edm::ValueMap<float>& arguments to be called

  virtual void operator()(pat::Jet& outputJet, double value) const;

  virtual void print(std::ostream& stream) const;

  friend class JetExtendedProducer;

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::ValueMap<float>> token_;  
};

#endif
