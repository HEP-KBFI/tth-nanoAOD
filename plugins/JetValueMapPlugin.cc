
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
  JetValueMapPlugin(const edm::ParameterSet& cfg)
    : JetExtendedPluginBase(cfg)
    , src_(cfg.getParameter<edm::InputTag>("src"))
  {}
  ~JetValueMapPlugin() {}
  
  virtual void operator()(pat::Jet& outputJet) const { assert(0); } // CV: force second operator() implementation with pat::Jet& and const edm::ValueMap<float>& arguments to be called

  virtual void operator()(pat::Jet& outputJet, double value) const
  {
    addUserFloat(outputJet, label_, value);
  }

  virtual void print(std::ostream& stream) const 
  {
    stream << "<JetValueMapPlugin::print>:" << std::endl;
    stream << " label = " << label_ << std::endl;
    stream << " overwrite = " << overwrite_ << std::endl;
    stream << " src = " << src_.label() << std::endl;
  }

  friend class JetExtendedProducer;

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::ValueMap<float>> token_;  
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_EDM_PLUGIN(JetExtendedPluginFactory, JetValueMapPlugin, "JetValueMapPlugin");


