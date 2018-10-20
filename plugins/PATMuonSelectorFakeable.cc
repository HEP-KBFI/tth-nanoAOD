
/** \class PATMuonSelectorFakeable
 *
 * Produce collection of pat::Muon objects passing fakeable lepton selection on ttH multilepton+tau analysis (HIG-18-019).
 * The collection of pat::Muon is used to clean the collection of packedPFCandidates, 
 * which is used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008).
 *
 * WARNING: this code needs to match exactly https://github.com/HEP-KBFI/tth-htt/blob/master/src/RecoMuonCollectionSelectorFakeable.cc,
 *          except that the cuts on pT(lepton)/pT(jet) and on the CSVv2 b-tagging discriminant of nearby jets are disabled,
 *          in order to make the muon selection independent of nearby AK4 jets
 *
 * \author Christian Veelken, Tallinn
 *
 */

#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/Exception.h" 

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/Common/interface/Ptr.h"

#include <cmath>

enum { kEra_undefined, kEra_2016, kEra_2017, kEra_2018 };

class PATMuonSelectorFakeable : public edm::stream::EDProducer<>
{
 public:
  PATMuonSelectorFakeable(const edm::ParameterSet& cfg)
    : src_(cfg.getParameter<edm::InputTag>("src"))
    , src_mvaRawTTH_(cfg.getParameter<edm::InputTag>("src_mvaRawTTH"))
    , era_(kEra_undefined)
    , debug_(cfg.getParameter<bool>("debug"))
    , min_pt_(-1.e+3)
    , max_absEta_(2.4)
    , max_dxy_(0.05)
    , max_dz_(0.1)
    , max_relIso_(0.4)
    , max_sip3d_(8.)
    , apply_looseIdPOG_(true)
    , apply_mediumIdPOG_(false)
  {
    token_ = consumes<edm::View<pat::Muon>>(src_);
    token_mvaRawTTH_ = consumes<edm::ValueMap<float>>(src_mvaRawTTH_);

    std::string era_string = cfg.getParameter<std::string>("era");
    if      ( era_string == "2016" ) era_ = kEra_2016;
    else if ( era_string == "2017" ) era_ = kEra_2017;
    //else if ( era_string == "2018" ) era_ = kEra_2018;
    else throw cms::Exception("PATMuonSelectorFakeable")
      << "Invalid Configuration parameter 'era' = " << era_string << " !!\n";
    switch ( era_ ) {
      case kEra_2016: {
	min_pt_ = 10.;
	binning_mvaTTH_ = { 0.75 };
	min_segmentCompatibility_ = { -1.e+3, -1.e+3 }; 
	break;
      }
      case kEra_2017: {
	min_pt_ = 5.; 
	binning_mvaTTH_ = { 0.90 };
	min_segmentCompatibility_ = { 0.3, -1.e+3 };
	break;
      }      
      //case kEra_2018: {
      //
      //}
      default: assert(0);
    }
    assert(min_pt_ > 0.);
    assert(binning_mvaTTH_.size() == 1);
    assert(min_segmentCompatibility_.size() == binning_mvaTTH_.size() + 1);

    produces<pat::MuonCollection>();
  }
  ~PATMuonSelectorFakeable() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<edm::View<pat::Muon>> inputMuons;
    evt.getByToken(token_, inputMuons);
    edm::Handle<edm::ValueMap<float>> inputMuons_mvaRawTTH;
    evt.getByToken(token_mvaRawTTH_, inputMuons_mvaRawTTH);

    std::unique_ptr<pat::MuonCollection> outputMuons(new pat::MuonCollection());

    for ( size_t inputMuons_idx = 0; inputMuons_idx < inputMuons->size(); ++inputMuons_idx ) {
      edm::Ptr<pat::Muon> muon = inputMuons->ptrAt(inputMuons_idx);
      if ( muon->pt() < min_pt_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS pT >= " << min_pt_ << " cut\n";
	}
	continue;
      }
      double absEta = std::fabs(muon->eta());
      if ( absEta > max_absEta_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(eta) <= " << max_absEta_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(muon->dB(pat::Muon::PV2D)) > max_dxy_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(dxy) <= " << max_dxy_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(muon->dB(pat::Muon::PVDZ)) > max_dz_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(dz) <= " << max_dz_ << " cut\n";
	}
	continue;
      }
      if ( muon->userFloat("miniIsoAll") > (max_relIso_*muon->pt()) ) {
	if ( debug_ ) {
	  std::cout << "FAILS relIso <= " << max_relIso_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(muon->dB(pat::Muon::PV3D)/muon->edB(pat::Muon::PV3D)) > max_sip3d_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS sip3d <= " << max_sip3d_ << " cut\n";
	}
	continue;
      }
      // KE: no need to apply cut on loose muon ID,
      //     as all muons on nanoAOD pass the loose muon ID
      //if ( apply_looseIdPOG_ && !muon->passesLooseIdPOG() ) {
      //  if ( debug_ ) {
      //    std::cout << "FAILS loose POG cut\n";
      //  }
      //  continue;
      //}
      if ( apply_mediumIdPOG_ && !muon->passed(reco::Muon::CutBasedIdMedium) ) {
	if ( debug_ ) {
	  std::cout << "FAILS medium POG cut\n";
	}
	continue;
      }
      double mvaRawTTH = (*inputMuons_mvaRawTTH)[muon];
      const int idxBin_mvaTTH = mvaRawTTH <= binning_mvaTTH_[0] ? 0 : 1;
      if ( muon->segmentCompatibility() <= min_segmentCompatibility_[idxBin_mvaTTH] ) {
	if ( debug_ ) {
	  std::cout << "FAILS segmentCompatibility > " << min_segmentCompatibility_[idxBin_mvaTTH] << " cut\n";
	}
	continue;
      }
      // CV: muon passes all cuts
      outputMuons->push_back(*muon);
    }
    
    evt.put(std::move(outputMuons));
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("PAT muon selector module for 'fakeable' leptons used in ttH multilepton+tau analysis (HIG-18-019)");
    desc.add<edm::InputTag>("src")->setComment("muon input collection");
    desc.add<edm::InputTag>("src_mvaRawTTH")->setComment("ttH lepton ID MVA input collection for muons");
    desc.add<edm::InputTag>("era")->setComment("run period");
    descriptions.add("PATMuonSelectorFakeable", desc);
  }

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::View<pat::Muon>> token_;  
  edm::InputTag src_mvaRawTTH_;
  edm::EDGetTokenT<edm::ValueMap<float>> token_mvaRawTTH_;

  int era_;
  bool debug_;
  bool apply_offline_e_trigger_cuts_;

  float min_pt_;                    ///< lower cut threshold on lepton pT
  float max_absEta_;                ///< upper cut threshold on absolute value of eta
  float max_dxy_;                   ///< upper cut threshold on d_{xy}, distance in the transverse plane w.r.t PV
  float max_dz_;                    ///< upper cut threshold on d_{z}, distance on the z axis w.r.t PV
  float max_relIso_;                ///< upper cut threshold on relative isolation
  float max_sip3d_;                 ///< upper cut threshold on significance of IP
  bool apply_looseIdPOG_;           ///< apply (True) or do not apply (False) loose PFMuon id selection
//-------------------------------------------------------------------------------
//--- define cuts that dependent on lepton MVA of ttH multilepton analysis 
//    format: muon fails / passes loose cut on lepton MVA value
  typedef std::vector<float> vfloat;  
  vfloat binning_mvaTTH_;        ///< lepton MVA threshold
//-------------------------------------------------------------------------------
  bool apply_mediumIdPOG_;          ///< apply (True) or do not apply (False) medium PFMuon id selection
  vfloat min_segmentCompatibility_; ///< upper cut threshold on compatibility of muon track segments with signature expected for muons
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(PATMuonSelectorFakeable);
