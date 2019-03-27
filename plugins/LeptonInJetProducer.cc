// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/global/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "fastjet/PseudoJet.hh"
#include <fastjet/JetDefinition.hh>
#include <TLorentzVector.h>
#include <TMath.h>

template <typename T>
class LeptonInJetProducer : public edm::global::EDProducer<> {
public:
  explicit LeptonInJetProducer(const edm::ParameterSet &iConfig) :
    srcPF_(consumes<pat::PackedCandidateCollection>(iConfig.getParameter<edm::InputTag>("srcPF"))),
    srcJet_(consumes<edm::View<pat::Jet>>(iConfig.getParameter<edm::InputTag>("src"))),
    srcEle_(consumes<edm::View<pat::Electron>>(iConfig.getParameter<edm::InputTag>("srcEle"))),
    srcMu_(consumes<edm::View<pat::Muon>>(iConfig.getParameter<edm::InputTag>("srcMu")))
  {
    produces<edm::ValueMap<float>>("lsf3");
    produces<edm::ValueMap<float>>("lsf3match");
    produces<edm::ValueMap<int>>("lep3idmatch");
    produces<edm::ValueMap<int>>("lep3indexmatch");
  }
  ~LeptonInJetProducer() override {};
  
  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
  
private:
  void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override ;

  static bool orderPseudoJet(fastjet::PseudoJet j1, fastjet::PseudoJet j2);
  std::tuple<float,float> calculateLSF(std::vector<fastjet::PseudoJet> iCParticles, std::vector<fastjet::PseudoJet> &ljets,
				       float ilPt, float ilEta, float ilPhi, int ilId, double dr, int nsj) const;

  edm::EDGetTokenT<pat::PackedCandidateCollection> srcPF_;
  edm::EDGetTokenT<edm::View<pat::Jet>> srcJet_;
  edm::EDGetTokenT<edm::View<pat::Electron>> srcEle_;
  edm::EDGetTokenT<edm::View<pat::Muon>> srcMu_;

};

// ------------ method called to produce the data  ------------
template <typename T>
void
LeptonInJetProducer<T>::produce(edm::StreamID streamID, edm::Event& iEvent, const edm::EventSetup& iSetup) const
{

    // needs PFcandidate collection (srcPF), jet collection (srcJet), leptons collection 
    edm::Handle<pat::PackedCandidateCollection> srcPF;
    iEvent.getByToken(srcPF_, srcPF);
    edm::Handle<edm::View<pat::Jet>> srcJet;
    iEvent.getByToken(srcJet_, srcJet);
    edm::Handle<edm::View<pat::Electron>> srcEle;
    iEvent.getByToken(srcEle_, srcEle);   
    edm::Handle<edm::View<pat::Muon>> srcMu;
    iEvent.getByToken(srcMu_, srcMu);

    unsigned int nJet = srcJet->size();
    unsigned int nEle = srcEle->size();
    unsigned int nMu  = srcMu->size();

    std::vector<float> *vlsf3 = new std::vector<float>;
    std::vector<float> *vlsf3match = new std::vector<float>;
    std::vector<int> *vlep3idmatch = new std::vector<int>;
    std::vector<int> *vlep3indexmatch = new std::vector<int>;

    // Matching electron and pfcands  
    const pat::PackedCandidate *ele_pfmatch = nullptr; int ele_pfmatch_index = -1;
    for (unsigned int il(0); il < nEle; il++) {
      auto itLep = srcEle->ptrAt(il);
      for (const pat::PackedCandidate &itPF : *srcPF) {
	for(unsigned int i1 = 0 ; i1 < itLep->numberOfSourceCandidatePtrs();i1++){
	  auto  c1s= itLep->sourceCandidatePtr(i1);
	  for(unsigned int i2 = 0 ; i2 < itPF.numberOfSourceCandidatePtrs();i2++) {
	    if(itPF.sourceCandidatePtr(i2)==c1s) { ele_pfmatch = &itPF; ele_pfmatch_index = i1; }
	  }
	}
      } 
    } 
    const pat::PackedCandidate *mu_pfmatch = nullptr; int mu_pfmatch_index = -1;
    for (unsigned int il(0); il < nMu; il++) {
      auto itLep = srcMu->ptrAt(il);
      for (const pat::PackedCandidate &itPF : *srcPF) {
	for(unsigned int i1 = 0 ; i1 < itLep->numberOfSourceCandidatePtrs();i1++){
          auto  c1s= itLep->sourceCandidatePtr(i1);
          for(unsigned int i2 = 0 ; i2 < itPF.numberOfSourceCandidatePtrs();i2++) {
	    if(itPF.sourceCandidatePtr(i2)==c1s) { mu_pfmatch = &itPF; mu_pfmatch_index = i1; }
	  }
	}
      } 
    } 

    // Find leptons in jets
    for (unsigned int ij = 0; ij<nJet; ij++){
      const pat::Jet &itJet = (*srcJet)[ij];
      if(itJet.pt() <= 10) continue;
      std::vector<fastjet::PseudoJet> lClusterParticles;
      float lepPt(-1),lepEta(-1),lepPhi(-1);
      int lepId(-1),lepIndex(-1);
      for (auto const d : itJet.daughterPtrVector() ) {
	fastjet::PseudoJet p( d->px(), d->py(), d->pz(), d->energy() );
        lClusterParticles.emplace_back(p);
	if(fabs(d->pdgId()) != 11 && fabs(d->pdgId()) != 13) continue;
	if(d->pt() > lepPt) { 
	  lepPt = d->pt();
	  lepEta = d->eta();
	  lepPhi = d->phi();
	  lepId = fabs(d->pdgId());
	}
      }

      std::sort(lClusterParticles.begin(),lClusterParticles.end(),orderPseudoJet);
      std::vector<fastjet::PseudoJet> psub_3; 
      auto lsf_3 = calculateLSF(lClusterParticles, psub_3, lepPt, lepEta, lepPhi, lepId, 2.0, 3);
      vlsf3->push_back( std::get<0>(lsf_3));

      double dRmin(0.8),dRele(999),dRmu(999);
      if(ele_pfmatch!=nullptr) dRele = reco::deltaR(itJet.eta(), itJet.phi(), ele_pfmatch->eta(), ele_pfmatch->phi());
      if(mu_pfmatch!=nullptr) dRmu = reco::deltaR(itJet.eta(), itJet.phi(), mu_pfmatch->eta(), mu_pfmatch->phi());
      lepPt=-1; lepEta=-1; lepPhi=-1;
      lepId=-1; lepIndex=-1;
      if(dRele < dRmin) {
	lepPt = ele_pfmatch->pt();
	lepEta = ele_pfmatch->eta();
	lepPhi = ele_pfmatch->phi();
	lepId = 11;
        lepIndex = ele_pfmatch_index;
      }
      if(dRmu < dRmin && dRmu < dRele) {
	lepPt = mu_pfmatch->pt();
        lepEta = mu_pfmatch->eta();
        lepPhi = mu_pfmatch->phi();
        lepId = 13;
	lepIndex = mu_pfmatch_index;
      } 
      std::vector<fastjet::PseudoJet> psub_3match;
      auto lsf_3match = calculateLSF(lClusterParticles, psub_3match, lepPt, lepEta, lepPhi, lepId, 2.0, 3);
      vlsf3match->push_back( std::get<0>(lsf_3match));
      vlep3idmatch->push_back( lepId );
      vlep3indexmatch->push_back( lepIndex );
    }


    // Filling table
    std::unique_ptr<edm::ValueMap<float>> lsf3V(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillerlsf3(*lsf3V);
    fillerlsf3.insert(srcJet,vlsf3->begin(),vlsf3->end());
    fillerlsf3.fill();
    iEvent.put(std::move(lsf3V),"lsf3");

    std::unique_ptr<edm::ValueMap<float>> lsf3matchV(new edm::ValueMap<float>());
    edm::ValueMap<float>::Filler fillerlsf3match(*lsf3matchV);
    fillerlsf3match.insert(srcJet,vlsf3match->begin(),vlsf3match->end());
    fillerlsf3match.fill();
    iEvent.put(std::move(lsf3matchV),"lsf3match");

    std::unique_ptr<edm::ValueMap<int>> lep3idmatchV(new edm::ValueMap<int>());
    edm::ValueMap<int>::Filler fillerlep3idmatch(*lep3idmatchV);
    fillerlep3idmatch.insert(srcJet,vlep3idmatch->begin(),vlep3idmatch->end());
    fillerlep3idmatch.fill();
    iEvent.put(std::move(lep3idmatchV),"lep3idmatch");

    std::unique_ptr<edm::ValueMap<int>> lep3indexmatchV(new edm::ValueMap<int>());
    edm::ValueMap<int>::Filler fillerlep3indexmatch(*lep3indexmatchV);
    fillerlep3indexmatch.insert(srcJet,vlep3indexmatch->begin(),vlep3indexmatch->end());
    fillerlep3indexmatch.fill();
    iEvent.put(std::move(lep3indexmatchV),"lep3indexmatch");

}

template <typename T>
bool LeptonInJetProducer<T>::orderPseudoJet(fastjet::PseudoJet j1, fastjet::PseudoJet j2) {
  return j1.perp2() > j2.perp2();
}

template <typename T>
std::tuple<float,float> LeptonInJetProducer<T>::calculateLSF(std::vector<fastjet::PseudoJet> iCParticles, std::vector<fastjet::PseudoJet> &lsubjets, 
							     float ilPt, float ilEta, float ilPhi, int ilId, double dr, int nsj) const {
  float lsf(-1),lmd(-1);
  if(ilPt>0 && (ilId == 11 || ilId == 13)) {    
    TLorentzVector ilep; 
    if(ilId == 11) ilep.SetPtEtaPhiM(ilPt, ilEta, ilPhi, 0.000511);
    if(ilId == 13) ilep.SetPtEtaPhiM(ilPt, ilEta, ilPhi, 0.105658);
    fastjet::JetDefinition lCJet_def(fastjet::kt_algorithm, dr);
    fastjet::ClusterSequence lCClust_seq(iCParticles, lCJet_def);
    if (dr > 0.5) {
      lsubjets = sorted_by_pt(lCClust_seq.exclusive_jets_up_to(nsj));
    }
    else {
      lsubjets = sorted_by_pt(lCClust_seq.inclusive_jets());
    }
    int lId(-1);
    double dRmin = 999.;
    for (unsigned int i0=0; i0<lsubjets.size(); i0++) {
      double dR = reco::deltaR(lsubjets[i0].eta(), lsubjets[i0].phi(), ilep.Eta(), ilep.Phi());
      if ( dR < dRmin ) {
	dRmin = dR;
	lId = i0;
	}
    }
    if(lId != -1) {
      TLorentzVector pVec; pVec.SetPtEtaPhiM(lsubjets[lId].pt(), lsubjets[lId].eta(), lsubjets[lId].phi(), lsubjets[lId].m());
      lsf = ilep.Pt()/pVec.Pt();
      lmd = (ilep-pVec).M()/pVec.M();
    }
  }
  return std::tuple<float,float>(lsf,lmd);
}

template <typename T>
void LeptonInJetProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("srcPF")->setComment("candidate input collection");
  desc.add<edm::InputTag>("src")->setComment("jet input collection");
  desc.add<edm::InputTag>("srcEle")->setComment("electron input collection");
  desc.add<edm::InputTag>("srcMu")->setComment("muon input collection");
  std::string modname;
  modname+="LepIn";
  if (typeid(T) == typeid(pat::Jet)) modname+="Jet";
  modname+="Producer";
  descriptions.add(modname,desc);
}


typedef LeptonInJetProducer<pat::Jet> LepInJetProducer;

//define this as a plug-in
DEFINE_FWK_MODULE(LepInJetProducer);
