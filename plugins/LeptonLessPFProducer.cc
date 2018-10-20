
/** \class LeptonLessPFProducer
 *
 * Produce collection of packedPFCandidates not associated to fakeable electrons or muons,
 * used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008).
 *
 * WARNING: https://github.com/nickmccoll/AnalysisTreeMaker/blob/master/Utilities/plugins/LeptonLessPFProducer.cc
 *          except that no selection criteria are applied to electrons and muons
 *
 * \author Nickolas Mc Coll, UCLA;
 *         with modifications by Christian Veelken, Tallinn
 *
 */

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/Exception.h" 

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

class LeptonLessPFProducer : public edm::stream::EDProducer<> 
{
 public:
  LeptonLessPFProducer(const edm::ParameterSet& cfg)
    : src_pfCands_(cfg.getParameter<edm::InputTag>("src_pfCands"))
    , src_electrons_(cfg.getParameter<edm::InputTag>("src_electrons"))
    , src_muons_(cfg.getParameter<edm::InputTag>("src_muons"))
  {
    token_pfCands_ = consumes<pat::PackedCandidateCollection>(src_pfCands_);
    token_electrons_ = consumes<pat::ElectronCollection>(src_electrons_);
    token_muons_ = consumes<pat::MuonCollection>(src_muons_);
  }
  ~LeptonLessPFProducer() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<pat::PackedCandidateCollection> inputPFCands;
    evt.getByToken(token_pfCands_, inputPFCands);
    edm::Handle<pat::ElectronCollection> electrons;
    evt.getByToken(token_electrons_, electrons);
    edm::Handle<pat::MuonCollection> muons;
    evt.getByToken(token_muons_, muons);
    
    std::unique_ptr<pat::PackedCandidateCollection> outputPFCands(new pat::PackedCandidateCollection());

    std::vector<unsigned int> filteredPFCandidateList;

    for ( pat::ElectronCollection::const_iterator electron = electrons->begin();
	  electron != electrons->end(); ++electron ) {
      for ( unsigned int idxPFCand = 0; idxPFCand < electron->associatedPackedPFCandidates().size(); ++idxPFCand ) {
	int absPdgId = std::abs(electron->associatedPackedPFCandidates()[idxPFCand]->pdgId());
	if ( absPdgId == 11 || absPdgId == 211 || absPdgId == 22 ) {
	  if ( debug_ ) {
	    std::cout << "associating PFCandidate #" << electron->associatedPackedPFCandidates()[idxPFCand].key() << " to electron." << std::endl;
	  }
	  filteredPFCandidateList.push_back(electron->associatedPackedPFCandidates()[idxPFCand].key());
	}
      }
    }

    for ( pat::MuonCollection::const_iterator muon = muons->begin();
	  muon != muons->end(); ++muon ) {
      if ( muon->originalObjectRef().isNull() ) {
	std::cout << "muon with pT = " << muon->pt() << ", eta = " << muon->eta() << ", phi = " << muon->phi() << " has NULL reference to PFCandidate collection !!" << std::endl;
	continue;
      }
      if ( muon->originalObjectRef().id() != inputPFCands.id() ) {
	std::cout << "muon with pT = " << muon->pt() << ", eta = " << muon->eta() << ", phi = " << muon->phi() << " has reference to different PFCandidate collection !!" << std::endl;
	continue;
      }
      if ( debug_ ) {
	std::cout << "associating PFCandidate #" << muon->originalObjectRef().key() << " to muon." << std::endl;
      }
      filteredPFCandidateList.push_back(muon->originalObjectRef().key());
    }

    for ( size_t inputPFCand_idx = 0; inputPFCand_idx < inputPFCands->size(); ++inputPFCand_idx ) {
      const pat::PackedCandidate& pfCand = inputPFCands->at(inputPFCand_idx);
      bool found = false;
      for ( std::vector<unsigned int>::const_iterator filteredPFCandidate = filteredPFCandidateList.begin();
	    filteredPFCandidate != filteredPFCandidateList.end(); ++filteredPFCandidate ) {
	if ( inputPFCand_idx == (*filteredPFCandidate) ) {
	  found = true; 
	  break;
	}
      }
      if ( !found ) outputPFCands->push_back(pfCand);
    }
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("Produce collection of packedPFCandidates used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008)");
    desc.add<edm::InputTag>("src_pfCands")->setComment("packedPFCandidate input collection");
    desc.add<edm::InputTag>("src_electrons")->setComment("electron input collection");
    desc.add<edm::InputTag>("src_muons")->setComment("muon input collection");
    descriptions.add("LeptonLessPFProducer", desc);
  }

 private:
  edm::InputTag src_pfCands_;
  edm::EDGetTokenT<pat::PackedCandidateCollection> token_pfCands_;  
  edm::InputTag src_electrons_;
  edm::EDGetTokenT<pat::ElectronCollection> token_electrons_;  
  edm::InputTag src_muons_;
  edm::EDGetTokenT<pat::MuonCollection> token_muons_;  

  bool debug_;
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(LeptonLessPFProducer);
