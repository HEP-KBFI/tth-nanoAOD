#include "tthAnalysis/NanoAOD/interface/JetValueMapPlugin.h"

JetValueMapPlugin::JetValueMapPlugin(const edm::ParameterSet& cfg)
  : JetExtendedPluginBase(cfg)
  , src_(cfg.getParameter<edm::InputTag>("src"))
{}

JetValueMapPlugin::~JetValueMapPlugin() 
{}
  
void JetValueMapPlugin::operator()(pat::Jet& outputJet, double value) const
{
  addUserFloat(outputJet, label_, value);
}

void JetValueMapPlugin::print(std::ostream& stream) const 
{
  stream << "<JetValueMapPlugin::print>:" << std::endl;
  stream << " label = " << label_ << std::endl;
  stream << " overwrite = " << overwrite_ << std::endl;
  stream << " src = " << src_.label() << std::endl;
}

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_EDM_PLUGIN(JetExtendedPluginFactory, JetValueMapPlugin, "JetValueMapPlugin");


