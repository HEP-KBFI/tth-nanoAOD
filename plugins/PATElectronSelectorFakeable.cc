
/** \class PATElectronSelectorFakeable
 *
 * Produce collection of pat::Electron objects passing fakeable lepton selection on ttH multilepton+tau analysis (HIG-18-019).
 * The collection of pat::Electrons is used to clean the collection of packedPFCandidates, 
 * which is used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008).
 *
 * WARNING: this code needs to match exactly https://github.com/HEP-KBFI/tth-htt/blob/master/src/RecoElectronCollectionSelectorFakeable.cc,
 *          except that the cuts on pT(lepton)/pT(jet) and on the CSVv2 b-tagging discriminant of nearby jets are disabled,
 *          in order to make the electron selection independent of nearby AK4 jets
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

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/Common/interface/Ptr.h"

#include <cmath>

enum { kEra_undefined, kEra_2016, kEra_2017, kEra_2018 };

class PATElectronSelectorFakeable : public edm::stream::EDProducer<>
{
 public:
  PATElectronSelectorFakeable(const edm::ParameterSet& cfg)
    : src_(cfg.getParameter<edm::InputTag>("src"))
    , src_mvaRawTTH_(cfg.getParameter<edm::InputTag>("src_mvaRawTTH"))
    , era_(kEra_undefined)
    , debug_(cfg.getParameter<bool>("debug"))
    , apply_offline_e_trigger_cuts_(true)
    , min_pt_(-1.e+3)
    , max_absEta_(2.5)
    , max_dxy_(0.05) 
    , max_dz_(0.1)
    , max_relIso_(0.4)
    , max_sip3d_(8.) 
    , min_OoEminusOoP_trig_(-1.e+3)
    , apply_conversionVeto_(true)
    , max_nLostHits_(0)
  {
    token_ = consumes<edm::View<pat::Electron>>(src_);
    token_mvaRawTTH_ = consumes<edm::ValueMap<float>>(src_mvaRawTTH_);

    std::string era_string = cfg.getParameter<std::string>("era");
    if      ( era_string == "2016" ) era_ = kEra_2016;
    else if ( era_string == "2017" ) era_ = kEra_2017;
    //else if ( era_string == "2018" ) era_ = kEra_2018;
    else throw cms::Exception("PATElectronSelectorFakeable")
      << "Invalid Configuration parameter 'era' = " << era_string << " !!\n";
    switch ( era_ ) {
      case kEra_2016: {
	min_pt_ = 10.;
	binning_absEta_ = { 0.8, 1.479 };
	min_pt_trig_ = 30.;
	max_sigmaEtaEta_trig_ = { 0.011, 0.011, 0.030 };
	max_HoE_trig_ = { 0.10, 0.10, 0.07 };
	max_deltaEta_trig_ = { 0.01, 0.01, 0.008 };
	max_deltaPhi_trig_ = { 0.04, 0.04, 0.07 };
	min_OoEminusOoP_trig_ = -0.05;
	max_OoEminusOoP_trig_ = { 0.010, 0.010, 0.005 };
	binning_mvaTTH_ = { 0.75 };
	min_mvaIDraw_ = { -1.e+3, -1.e+3 };
	break;
      }
      case kEra_2017: {
	min_pt_ = 7.;
	binning_absEta_ = { 1.479 }; 
	min_pt_trig_ = -1.; // LFR sync; used to be 30 GeV (cf. lines 237-240 in AN-2017/029 v5)
	max_sigmaEtaEta_trig_ = { 0.011, 0.030 };
	max_HoE_trig_ = { 0.10, 0.10 }; 
	max_deltaEta_trig_ = { +1.e+3, +1.e+3 }; 
	max_deltaPhi_trig_ = { +1.e+3, +1.e+3 };
	min_OoEminusOoP_trig_ = -0.04; 
	max_OoEminusOoP_trig_ = { +1.e+3, +1.e+3 }; 
	binning_mvaTTH_ = { 0.90 }; 
	min_mvaIDraw_ = { 0.50, -1.e+3 }; 
	break;
      }      
      //case kEra_2018: {
      //
      //}
      default: assert(0);
    }
    assert(min_pt_ > 0.);
    assert(binning_absEta_.size() > 0);
    assert(max_sigmaEtaEta_trig_.size() == binning_absEta_.size() + 1);
    assert(max_HoE_trig_.size() == binning_absEta_.size() + 1);
    assert(max_deltaEta_trig_.size() == binning_absEta_.size() + 1);
    assert(max_deltaPhi_trig_.size() == binning_absEta_.size() + 1);
    assert(max_OoEminusOoP_trig_.size() == binning_absEta_.size() + 1);
    assert(binning_mvaTTH_.size() == 1);
    assert(min_mvaIDraw_.size() == binning_mvaTTH_.size() + 1);

    produces<pat::ElectronCollection>();
  }
  ~PATElectronSelectorFakeable() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<edm::View<pat::Electron>> inputElectrons;
    evt.getByToken(token_, inputElectrons);
    edm::Handle<edm::ValueMap<float>> inputElectrons_mvaRawTTH;
    evt.getByToken(token_mvaRawTTH_, inputElectrons_mvaRawTTH);

    std::unique_ptr<pat::ElectronCollection> outputElectrons(new pat::ElectronCollection());

    for ( size_t inputElectrons_idx = 0; inputElectrons_idx < inputElectrons->size(); ++inputElectrons_idx ) {
      edm::Ptr<pat::Electron> electron = inputElectrons->ptrAt(inputElectrons_idx);
      if ( electron->pt() < min_pt_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS pT >= " << min_pt_ << " cut\n";
	}
	continue;
      }
      double absEta = std::fabs(electron->eta());
      if ( absEta > max_absEta_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(eta) <= " << max_absEta_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(electron->dB(pat::Electron::PV2D)) > max_dxy_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(dxy) <= " << max_dxy_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(electron->dB(pat::Electron::PVDZ)) > max_dz_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS abs(dz) <= " << max_dz_ << " cut\n";
	}
	continue;
      }
      if ( electron->userFloat("miniIsoAll") > (max_relIso_*electron->pt()) ) {
	if ( debug_ ) {
	  std::cout << "FAILS relIso <= " << max_relIso_ << " cut\n";
	}
	continue;
      }
      if ( std::fabs(electron->dB(pat::Electron::PV3D)/electron->edB(pat::Electron::PV3D)) > max_sip3d_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS sip3d <= " << max_sip3d_ << " cut\n";
	}
	continue;
      }
      if ( electron->gsfTrack().isNull() || electron->gsfTrack()->hitPattern().numberOfLostHits(reco::HitPattern::MISSING_INNER_HITS) > max_nLostHits_ ) {
	if ( debug_ ) {
	  std::cout << "FAILS nLostHits <= " << max_nLostHits_ << " cut\n";
	}
	continue;
      }
      if ( apply_conversionVeto_ && !electron->passConversionVeto() ) {
	if ( debug_ ) {
	  std::cout << "FAILS conversion veto\n";
	}
	continue;
      }
      if ( !electron->userInt("mvaFall17noIso_WPL") ) {
	if ( debug_ ) {
	  std::cout << "FAILS EGamma POG MVA cut\n";
	}
	continue;
      }
      double mvaRawTTH = (*inputElectrons_mvaRawTTH)[electron];
      const int idxBin_mvaTTH = mvaRawTTH <= binning_mvaTTH_[0] ? 0 : 1;
      if ( electron->userFloat("mvaFall17noIso") < min_mvaIDraw_[idxBin_mvaTTH] ) {
	if ( debug_ ) {
	  std::cout << "FAILS EGamma POG MVA raw >= " << min_mvaIDraw_[idxBin_mvaTTH] << " cut\n";
	}
	continue;
      }
      if ( apply_offline_e_trigger_cuts_ && electron->pt() > min_pt_trig_ ) {
	std::size_t idxBin_absEta = binning_absEta_.size();
	for ( std::size_t binning_absEta_idx = 0; binning_absEta_idx < binning_absEta_.size(); ++binning_absEta_idx ) {
	  if ( absEta <= binning_absEta_[binning_absEta_idx] ) {
	    idxBin_absEta = binning_absEta_idx;
	    break;
	  }
	}
	if ( electron->full5x5_sigmaIetaIeta() > max_sigmaEtaEta_trig_[idxBin_absEta] ) {
	  if ( debug_ ) {
	    std::cout << "FAILS sigmaEtaEta <= " << max_sigmaEtaEta_trig_[idxBin_absEta] << " cut\n";
	  }
	  continue;
	}
	if ( electron->hadronicOverEm() > max_HoE_trig_[idxBin_absEta] ) {
	  if ( debug_ ) {
	    std::cout << "FAILS HoE <= " << max_HoE_trig_[idxBin_absEta] << " cut\n";
	  }
	  continue;
	}
	if ( std::fabs(electron->deltaEtaSuperClusterTrackAtVtx()) > max_deltaEta_trig_[idxBin_absEta] ) {
	  if ( debug_ ) {
	    std::cout << "FAILS abs(deltaEta) <= " << max_deltaEta_trig_[idxBin_absEta] << " cut\n";
	  }
	  continue;
	}
	if ( std::fabs(electron->deltaPhiSuperClusterTrackAtVtx()) > max_deltaPhi_trig_[idxBin_absEta] ) {
	  if ( debug_ ) {
	    std::cout << "FAILS abs(deltaPhi) <= " << max_deltaPhi_trig_[idxBin_absEta] << " cut\n";
	  }
	  continue;
	}
	double OoEminusOoP = (1 - electron->eSuperClusterOverP())/electron->ecalEnergy();
	if ( OoEminusOoP < min_OoEminusOoP_trig_ ) {
	  if ( debug_ ) {
	    std::cout << "FAILS OoEminusOoP >= " << min_OoEminusOoP_trig_ << " cut\n";
	  }
	  continue;
	}
	if ( OoEminusOoP > max_OoEminusOoP_trig_[idxBin_absEta] ) {
	  if ( debug_ ) {
	    std::cout << "FAILS OoEminusOoP <= " << max_OoEminusOoP_trig_[idxBin_absEta] << " cut\n";
	  }
	  continue;
	}
      }
      // CV: electron passes all cuts
      outputElectrons->push_back(*electron);
    }
    
    evt.put(std::move(outputElectrons));
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("PAT electron selector module for 'fakeable' leptons used in ttH multilepton+tau analysis (HIG-18-019)");
    desc.add<edm::InputTag>("src")->setComment("electron input collection");
    desc.add<edm::InputTag>("src_mvaRawTTH")->setComment("ttH lepton ID MVA input collection for electrons");
    desc.add<edm::InputTag>("era")->setComment("run period");
    descriptions.add("PATElectronSelectorFakeable", desc);
  }

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::View<pat::Electron>> token_;  
  edm::InputTag src_mvaRawTTH_;
  edm::EDGetTokenT<edm::ValueMap<float>> token_mvaRawTTH_;

  int era_;
  bool debug_;
  bool apply_offline_e_trigger_cuts_;

  float min_pt_;                ///< lower cut threshold on lepton pT
  float max_absEta_;            ///< upper cut threshold on absolute value of eta
  float max_dxy_;               ///< upper cut threshold on d_{xy}, distance in the transverse plane w.r.t PV
  float max_dz_;                ///< upper cut threshold on d_{z}, distance on the z axis w.r.t PV
  float max_relIso_;            ///< upper cut threshold on relative isolation
  float max_sip3d_;             ///< upper cut threshold on significance of IP
//--- define cuts that dependent on eta
//    format: central region (|eta| < 0.8) / transition region (0.8 < |eta| < 1.479) / forward region (|eta| > 1.479)
  typedef std::vector<float> vfloat;
  vfloat binning_absEta_;       ///< eta values separating central, transition and forward region (0.8, 1.479)
  float min_pt_trig_;           ///< lower pT threshold for applying shower shape cuts (to mimic selection applied on trigger level)
  vfloat max_sigmaEtaEta_trig_; ///< upper cut threshold on second shower moment in eta-direction 
  vfloat max_HoE_trig_;         ///< upper cut threshold on ratio of energy deposits in hadronic/electromagnetic section of calorimeter
  vfloat max_deltaEta_trig_;    ///< upper cut threshold on difference in eta between impact position of track and electron cluster
  vfloat max_deltaPhi_trig_;    ///< upper cut threshold on difference in phi between impact position of track and electron cluster
  float min_OoEminusOoP_trig_;  ///< lower cut threshold on difference between calorimeter energy and track momentum (1/E - 1/P)
  vfloat max_OoEminusOoP_trig_; ///< upper cut threshold on difference between calorimeter energy and track momentum (1/E - 1/P)
//-------------------------------------------------------------------------------
//--- define cuts that dependent on lepton MVA of ttH multilepton analysis 
//    format: electron fails / passes loose cut on lepton MVA value
  vfloat binning_mvaTTH_;       ///< lepton MVA threshold
  vfloat min_mvaIDraw_;         ///< lower cut on EGamma POG MVA raw value
//-------------------------------------------------------------------------------
  bool apply_conversionVeto_;   ///< apply (True) or do not apply (False) conversion veto
  int max_nLostHits_;           ///< upper cut threshold on lost hits in the innermost layer of the tracker (electrons with lost_hits equal to cut threshold pass) 
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(PATElectronSelectorFakeable);
