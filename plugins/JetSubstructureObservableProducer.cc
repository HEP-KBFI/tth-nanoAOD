
/** \class JetSubstructureObservableProducer
 *
 * Produce collection of pat::Jet objects with different observables relevant for jet substructure analyses added as userFloats.
 * The userFloats are computed via plugins inheriting from JetExtendedPluginBase class.
 *
 * \author Christian Veelken, Tallinn
 * \author Karl Ehatäht, Tallinn
 *
 */

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/Common/interface/View.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/RefToBase.h"

#include "DataFormats/PatCandidates/interface/Jet.h"

class JetSubstructureObservableProducer
  : public edm::global::EDProducer<>
{
public:
  JetSubstructureObservableProducer(const edm::ParameterSet & cfg)
    : src_(consumes<edm::View<pat::Jet>>(cfg.getParameter<edm::InputTag>("src")))
    , kappa_(cfg.getParameter<double>("kappa"))
  {
    produces<edm::ValueMap<float>>("jetCharge");
    produces<edm::ValueMap<float>>("pullDEta");
    produces<edm::ValueMap<float>>("pullDPhi");
    produces<edm::ValueMap<float>>("pullDR");
  }
  ~JetSubstructureObservableProducer() {}

  void produce(edm::StreamID streamID, edm::Event& evt, const edm::EventSetup& es) const override
  {
    edm::Handle<edm::View<pat::Jet>> inputJets;
    evt.getByToken(src_, inputJets);

    const unsigned int nJet = inputJets->size();
    std::vector<float> charges(nJet, -2.);
    std::vector<float> pulls_dEta(nJet, -1.);
    std::vector<float> pulls_dPhi(nJet, -1.);
    std::vector<float> pulls_dR(nJet, -1.);

    for ( unsigned int iJet = 0; iJet < nJet; ++iJet ) {
      auto jet = inputJets->ptrAt(iJet);
      const float charge = calculateCharge(jet);
      const std::tuple<float, float, float> pulls = calculatePull(jet);
      const float pull_dEta = std::get<0>(pulls);
      const float pull_dPhi = std::get<1>(pulls);
      const float pull_dR = std::get<2>(pulls);

      charges[iJet] = charge;
      pulls_dEta[iJet] = pull_dEta;
      pulls_dPhi[iJet] = pull_dPhi;
      pulls_dR[iJet] = pull_dR;
    }

    std::unique_ptr<edm::ValueMap<float>> chargesV(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillCharges(*chargesV);
    fillCharges.insert(inputJets, charges.begin(), charges.end());
    fillCharges.fill();
    evt.put(std::move(chargesV),"jetCharge");

    std::unique_ptr<edm::ValueMap<float>> pulls_dEtaV(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillPulls_dEta(*pulls_dEtaV);
    fillPulls_dEta.insert(inputJets, pulls_dEta.begin(), pulls_dEta.end());
    fillPulls_dEta.fill();
    evt.put(std::move(pulls_dEtaV),"pullDEta");

    std::unique_ptr<edm::ValueMap<float>> pulls_dPhiV(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillPulls_dPhi(*pulls_dPhiV);
    fillPulls_dPhi.insert(inputJets, pulls_dPhi.begin(), pulls_dPhi.end());
    fillPulls_dPhi.fill();
    evt.put(std::move(pulls_dPhiV),"pullDPhi");

    std::unique_ptr<edm::ValueMap<float>> pulls_dRV(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillPulls_dR(*pulls_dRV);
    fillPulls_dR.insert(inputJets, pulls_dR.begin(), pulls_dR.end());
    fillPulls_dR.fill();
    evt.put(std::move(pulls_dRV),"pullDR");
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("Jet substructure observable producer");
    desc.add<edm::InputTag>("src")->setComment("jet input collection");
    desc.add<double>("kappa", 1.)->setComment("Exponent used to compute jet charge (specific to JetChargePlugin)");
    descriptions.add("JetSubstructureObservableProducer", desc);
  }

private:
  edm::EDGetTokenT<edm::View<pat::Jet>> src_;
  double kappa_;

  float calculateCharge(edm::Ptr<pat::Jet> const & jet) const {
    const std::vector<const reco::Candidate *> jetConstituents = jet->getJetConstituentsQuick();

    double sumCharge = 0.;
    double sumPt = 0.;
    for(const reco::Candidate * jetConstituent: jetConstituents)
    {
      const double jetConstituentCharge = jetConstituent->charge();
      const double jetConstituentPt = jetConstituent->pt();
      if(std::fabs(jetConstituentCharge) > 0.5)
      {
        sumCharge += jetConstituentCharge * std::pow(jetConstituentPt, kappa_);
      }
      sumPt += jetConstituentPt;
    }
    return sumPt > 0. ? sumCharge / std::pow(sumPt, kappa_) : 0.;
  }

  std::tuple<float,float,float> calculatePull(edm::Ptr<pat::Jet> const & jet) const {
    const double jetEta = jet->eta();
    const double jetPhi = jet->phi();
    const std::vector<const reco::Candidate *> jetConstituents = jet->getJetConstituentsQuick();

    double averageDEta = 0.;
    double averageDPhi = 0.;
    double sumWeights_1 = 0.;
    for(const reco::Candidate * jetConstituent: jetConstituents)
    {
      const double jetConstituentPt = jetConstituent->pt();
      const double dEta = jetConstituent->eta() - jetEta;
      const double dPhi = deltaPhi(jetConstituent->phi(), jetPhi);
      // CV: weight by pT^2, according to
      // https://github.com/amarini/VPlusJets/blob/40bae65f8eece1e602f1c45d1dc48099c91d07f8/plugins/JetExtendedProducer.cc#L211
      const double weight = jetConstituentPt * jetConstituentPt;

      averageDEta += (weight * dEta);
      averageDPhi += (weight * dPhi);
      sumWeights_1 += weight;
    }
    if(sumWeights_1 > 0.)
    {
      averageDEta /= sumWeights_1;
      averageDPhi /= sumWeights_1;
    }

    double sumDEta = 0.;
    double sumDPhi = 0.;
    double sumWeights_2 = 0.;
    for(const reco::Candidate * jetConstituent: jetConstituents)
    {
      const double jetConstituentPt = jetConstituent->pt();
      // CV: subtract average dEta and average dPhi, following
      // https://github.com/amarini/VPlusJets/blob/40bae65f8eece1e602f1c45d1dc48099c91d07f8/plugins/JetExtendedProducer.cc#L292-L293
      const double dEta = (jetConstituent->eta() - jetEta) - averageDEta;
      double dPhi = deltaPhi(jetConstituent->phi(), jetPhi) - averageDPhi;
      if(dPhi < -M_PI) dPhi += 2.*M_PI;
      if(dPhi > +M_PI) dPhi -= 2.*M_PI;

      const double weight = jetConstituentPt * jetConstituentPt;
      const double dR = std::sqrt(dEta * dEta + dPhi * dPhi);

      sumDEta += (dR * dEta * weight);
      sumDPhi += (dR * dPhi * weight);
      sumWeights_2 += weight;
    }
    if(sumWeights_2 > 0.)
    {
      sumDEta /= sumWeights_2;
      sumDPhi /= sumWeights_2;
    }
    const double sumDR = std::sqrt(sumDEta * sumDEta + sumDPhi * sumDPhi);

    return std::tuple<float,float,float>(sumDEta, sumDPhi, sumDR);
  }

};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(JetSubstructureObservableProducer);
