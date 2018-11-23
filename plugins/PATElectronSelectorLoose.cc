
/** \class PATElectronSelectorLoose
 *
 * Produce collection of pat::Electron objects passing loose lepton selection of ttH multilepton+tau analysis (HIG-18-019).
 * The collection of pat::Electrons is used to clean the collection of packedPFCandidates, 
 * which is used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008).
 *
 * WARNING: this code needs to match exactly https://github.com/HEP-KBFI/tth-htt/blob/master/src/RecoElectronCollectionSelectorLoose.cc,
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

class PATElectronSelectorLoose : public edm::stream::EDProducer<>
{
 public:
  PATElectronSelectorLoose(const edm::ParameterSet& cfg)
    : src_(cfg.getParameter<edm::InputTag>("src"))
    , era_(kEra_undefined)
    , debug_(cfg.getParameter<bool>("debug"))
    , min_pt_(-1.e+3)
    , max_absEta_(2.5)
    , max_dxy_(0.05) 
    , max_dz_(0.1)
    , max_relIso_(0.4)
    , max_sip3d_(8.) 
    , apply_conversionVeto_(false)
    , max_nLostHits_(1)
  {
    token_ = consumes<edm::View<pat::Electron>>(src_);

    std::string era_string = cfg.getParameter<std::string>("era");
    if      ( era_string == "2016" ) era_ = kEra_2016;
    else if ( era_string == "2017" ) era_ = kEra_2017;
    //else if ( era_string == "2018" ) era_ = kEra_2018;
    else throw cms::Exception("PATElectronSelectorLoose")
      << "Invalid Configuration parameter 'era' = " << era_string << " !!\n";
    switch ( era_ ) {
      case kEra_2016: {
        min_pt_ = 10.;
        binning_absEta_ = { 0.8, 1.479 };
        break;
      }
      case kEra_2017: {
        min_pt_ = 7.;
        binning_absEta_ = { 1.479 };
        break;
      }      
      //case kEra_2018: {
      //
      //}
      default: assert(0);
    }
    assert(min_pt_ > 0.);
    assert(binning_absEta_.size() > 0);

    produces<pat::ElectronCollection>();
  }
  ~PATElectronSelectorLoose() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<edm::View<pat::Electron>> inputElectrons;
    evt.getByToken(token_, inputElectrons);

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
      // CV: electron passes all cuts
      outputElectrons->push_back(*electron);
    }
    
    evt.put(std::move(outputElectrons));
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("PAT electron selector module for 'loose' leptons used in ttH multilepton+tau analysis (HIG-18-019)");
    desc.add<edm::InputTag>("src")->setComment("electron input collection");
    desc.add<edm::InputTag>("src_mvaTTH")->setComment("(unused)");
    desc.add<std::string>("era")->setComment("run period");
    desc.add<bool>("debug")->setComment("debug flag");
    descriptions.add("PATElectronSelectorLoose", desc);
  }

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::View<pat::Electron>> token_;

  int era_;
  bool debug_;

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
//-------------------------------------------------------------------------------
  bool apply_conversionVeto_;   ///< apply (True) or do not apply (False) conversion veto
  int max_nLostHits_;           ///< upper cut threshold on lost hits in the innermost layer of the tracker (electrons with lost_hits equal to cut threshold pass) 
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(PATElectronSelectorLoose);
