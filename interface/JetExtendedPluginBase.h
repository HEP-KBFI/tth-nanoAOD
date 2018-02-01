#ifndef tthAnalysis_NanoAOD_JetExtendedPluginBase_h
#define tthAnalysis_NanoAOD_JetExtendedPluginBase_h

/** \class JetExtendedPluginBase
 *
 * Base-class for adding observables relevant for jet substructure analyses as userFloats
 * to pat::Jet object
 *
 * \author Christian Veelken, Tallinn
 *
 */

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/Exception.h"

#include "DataFormats/PatCandidates/interface/Jet.h"

#include <string>
#include <iostream>
#include <iomanip>

class JetExtendedPluginBase
{
 public:
  JetExtendedPluginBase(const edm::ParameterSet& cfg) 
    : label_(cfg.getParameter<std::string>("label"))
    , overwrite_(cfg.exists("overwrite") ? cfg.getParameter<bool>("overwrite") : false)
  {}
  virtual ~JetExtendedPluginBase() {}

  virtual void operator()(pat::Jet& jet) const = 0;

  virtual void print(std::ostream&) const {}

 protected:
  virtual void addUserFloat(pat::Jet& jet, const std::string& label, double value) const
  {
    if ( jet.hasUserFloat(label) && !overwrite_ ) {
      throw cms::Exception("JetExtendedPluginBase")
	<< "UserFloat with label ='" << label << "' already exists in pat::Jet. Please enable overwrite !!\n";
    }
    jet.addUserFloat(label, value, overwrite_);
  }

  std::string label_;
  bool overwrite_;
};

#include "FWCore/PluginManager/interface/PluginFactory.h"

typedef edmplugin::PluginFactory<JetExtendedPluginBase* (const edm::ParameterSet&)> JetExtendedPluginFactory;

#endif



