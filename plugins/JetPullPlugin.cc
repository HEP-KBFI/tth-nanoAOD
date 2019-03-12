
/** \class JetPullPlugin
 *
 * Add jet "pull" observables (dEta, dPhi, and magnitude), computed according to Eq. (1) in arXiv:1001.5027,
 * to pat::Jet object
 * 
 * Note: the computation of the pull is not identical to the paper arXiv:1001.5027 in all details,
 *       but follows the implementation in https://github.com/amarini/VPlusJets/blob/master/plugins/JetExtendedProducer.cc
 *      (cf. https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html )
 *
 * \author Christian Veelken, Tallinn
 *
 */

#include "tthAnalysis/NanoAOD/interface/JetExtendedPluginBase.h"

#include "DataFormats/Math/interface/deltaPhi.h" // deltaPhi

#include <TMath.h> // TMath::Pi

#include <math.h> // sqrt

class JetPullPlugin : public JetExtendedPluginBase
{
 public:
  JetPullPlugin(const edm::ParameterSet& cfg)
    : JetExtendedPluginBase(cfg)
  {
    label_dEta_ = label_ + "_dEta";
    label_dPhi_ = label_ + "_dPhi";
    label_dR_ = label_ + "_dR";
  }
  ~JetPullPlugin() {}
  
  virtual void operator()(pat::Jet& jet) const
  {
    double jetEta = jet.eta();
    double jetPhi = jet.phi();
    std::vector<const reco::Candidate*> jetConstituents = jet.getJetConstituentsQuick();
    double averageDEta = 0.;
    double averageDPhi = 0.;
    double sumWeights_1 = 0.;
    for ( std::vector<const reco::Candidate*>::const_iterator jetConstituent = jetConstituents.begin();
          jetConstituent != jetConstituents.end(); ++jetConstituent ) {
      double jetConstituentPt = (*jetConstituent)->pt();
      double dEta = (*jetConstituent)->eta() - jetEta;
      double dPhi = deltaPhi((*jetConstituent)->phi(), jetPhi); 
      double weight = jetConstituentPt*jetConstituentPt; // CV: weight by pT^2, according to https://github.com/amarini/VPlusJets/blob/master/plugins/JetExtendedProducer.cc#L211
      averageDEta += (weight*dEta);
      averageDPhi += (weight*dPhi);
      sumWeights_1 += weight;
    }
    if ( sumWeights_1 > 0. ) {
      averageDEta /= sumWeights_1;
      averageDPhi /= sumWeights_1;
    }
    double sumDEta = 0.;
    double sumDPhi = 0.;
    double sumWeights_2 = 0.;
    for ( std::vector<const reco::Candidate*>::const_iterator jetConstituent = jetConstituents.begin();
          jetConstituent != jetConstituents.end(); ++jetConstituent ) {
      double jetConstituentPt = (*jetConstituent)->pt();
      // CV: subtract average dEta and average dPhi, following https://github.com/amarini/VPlusJets/blob/master/plugins/JetExtendedProducer.cc#L292-L293 
      double dEta = ((*jetConstituent)->eta() - jetEta) - averageDEta; 
      double dPhi = deltaPhi((*jetConstituent)->phi(), jetPhi) - averageDPhi; 
      if ( dPhi < -TMath::Pi() ) dPhi += 2.*TMath::Pi();
      if ( dPhi > +TMath::Pi() ) dPhi -= 2.*TMath::Pi();
      double weight = jetConstituentPt*jetConstituentPt;
      double dR = sqrt(dEta*dEta + dPhi*dPhi);
      sumDEta += (dR*dEta*weight);
      sumDPhi += (dR*dPhi*weight);
      sumWeights_2 += weight;
    }
    if ( sumWeights_2 > 0. ) {
      sumDEta /= sumWeights_2;
      sumDPhi /= sumWeights_2;
    }
    double sumDR = sqrt(sumDEta*sumDEta + sumDPhi*sumDPhi);
    addUserFloat(jet, label_dEta_, sumDEta);
    addUserFloat(jet, label_dPhi_, sumDPhi);
    addUserFloat(jet, label_dR_, sumDR);
  }

  virtual void print(std::ostream& stream) const 
  {
    stream << "<JetPullPlugin::print>:" << std::endl;
    stream << " label_dEta = " << label_dEta_ << std::endl;
    stream << " label_dPhi = " << label_dPhi_ << std::endl;
    stream << " label_dR = " << label_dR_ << std::endl;
    stream << " overwrite = " << overwrite_ << std::endl;
  }

 private:
  std::string label_dEta_;
  std::string label_dPhi_;
  std::string label_dR_;
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_EDM_PLUGIN(JetExtendedPluginFactory, JetPullPlugin, "JetPullPlugin");


