
/** \class JetChargePlugin
 *
 * Add (pT-weighted) jet charge, computed according to Eq. (4) in JME-13-006 PAS,
 * to pat::Jet object
 *
 * \author Christian Veelken, Tallinn
 *
 */

#include "tthAnalysis/NanoAOD/interface/JetExtendedPluginBase.h"

#include <cmath> // fabs
#include <math.h> // pow

class JetChargePlugin : public JetExtendedPluginBase
{
 public:
  JetChargePlugin(const edm::ParameterSet& cfg)
    : JetExtendedPluginBase(cfg)
    , kappa_(cfg.getParameter<double>("kappa"))
  {}
  ~JetChargePlugin() {}
  
  virtual void operator()(pat::Jet& jet) const
  {
    std::vector<const reco::Candidate*> jetConstituents = jet.getJetConstituentsQuick();
    double sumCharge = 0.;
    double sumPt = 0.;
    for ( std::vector<const reco::Candidate*>::const_iterator jetConstituent = jetConstituents.begin();
          jetConstituent != jetConstituents.end(); ++jetConstituent ) {
      double jetConstituentCharge = (*jetConstituent)->charge();
      double jetConstituentPt = (*jetConstituent)->pt();
      if ( fabs(jetConstituentCharge) > 0.5 ) {
        sumCharge += (jetConstituentCharge*pow(jetConstituentPt, kappa_));
      }
      sumPt += jetConstituentPt;
    }
    double jetCharge = ( sumPt > 0. ) ? sumCharge/pow(sumPt, kappa_) : 0.;
    addUserFloat(jet, label_, jetCharge);
  }

  virtual void print(std::ostream& stream) const 
  {
    stream << "<JetChargePlugin::print>:" << std::endl;
    stream << " label = " << label_ << std::endl;
    stream << " overwrite = " << overwrite_ << std::endl;
    stream << " kappa = " << kappa_ << std::endl;
  }

 private:
  double kappa_;
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_EDM_PLUGIN(JetExtendedPluginFactory, JetChargePlugin, "JetChargePlugin");


