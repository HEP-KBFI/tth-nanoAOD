
/** \class PATElectronSelectorFakeable
 *
 * Produce collection of pat::Electron objects passing fakeable lepton selection of ttH multilepton+tau analysis (HIG-18-019).
 * The collection of pat::Electrons is used to clean the collection of packedPFCandidates, 
 * which is used as input for the reconstruction of lepton subtracted AK8 jets (cf. B2G-18-008).
 *
 * WARNING: this code needs to match exactly https://github.com/HEP-KBFI/tth-htt/blob/master/src/RecoElectronCollectionSelectorFakeable.cc,
 *          except that the cuts on pT(lepton)/pT(jet) and on the b-tagging discriminant of nearby jets are disabled,
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

class PATElectronSelectorFakeable
  : public edm::stream::EDProducer<>
{
public:
  PATElectronSelectorFakeable(const edm::ParameterSet& cfg)
    : src_(cfg.getParameter<edm::InputTag>("src"))
    , src_mvaTTH_(cfg.getParameter<edm::InputTag>("src_mvaTTH"))
    , era_(kEra_undefined)
    , debug_(cfg.getParameter<bool>("debug"))
    , apply_offline_e_trigger_cuts_(true)
    , min_pt_(7.)
    , max_absEta_(2.5)
    , max_dxy_(0.05) 
    , max_dz_(0.1)
    , max_relIso_(0.4)
    , max_sip3d_(8.)
    , binning_absEta_(1.479)
    , min_sigmaEtaEta_trig_(0.011)
    , max_sigmaEtaEta_trig_(0.019)
    , max_HoE_trig_(0.10)
    , min_OoEminusOoP_trig_(-0.04)
    , wp_mvaTTH_(0.80)
    , apply_conversionVeto_(true)
    , max_nLostHits_(0)
  {
    token_ = consumes<edm::View<pat::Electron>>(src_);
    token_mvaTTH_ = consumes<edm::ValueMap<float>>(src_mvaTTH_);

    std::string era_string = cfg.getParameter<std::string>("era");
    if     (era_string == "2016") era_ = kEra_2016;
    else if(era_string == "2017") era_ = kEra_2017;
    else if(era_string == "2018") era_ = kEra_2018;
    else throw cms::Exception("PATElectronSelectorFakeable")
      << "Invalid Configuration parameter 'era' = " << era_string << '\n';

    produces<pat::ElectronCollection>();
  }
  ~PATElectronSelectorFakeable() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<edm::View<pat::Electron>> inputElectrons;
    evt.getByToken(token_, inputElectrons);
    edm::Handle<edm::ValueMap<float>> inputElectrons_mvaTTH;
    evt.getByToken(token_mvaTTH_, inputElectrons_mvaTTH);

    std::unique_ptr<pat::ElectronCollection> outputElectrons(new pat::ElectronCollection());

    for(std::size_t inputElectrons_idx = 0; inputElectrons_idx < inputElectrons->size(); ++inputElectrons_idx) {
      edm::Ptr<pat::Electron> electron = inputElectrons->ptrAt(inputElectrons_idx);
      if(electron->pt() < min_pt_) {
        if(debug_) {
          std::cout << "FAILS pT = " << electron->pt() << " >= " << min_pt_ << " cut\n";
        }
        continue;
      }
      const double absEta = std::fabs(electron->eta());
      if(absEta > max_absEta_) {
        if(debug_) {
          std::cout << "FAILS abs(eta) = " << absEta << " <= " << max_absEta_ << " cut\n";
        }
        continue;
      }
      const double absDxy = std::fabs(electron->dB(pat::Electron::PV2D));
      if(absDxy > max_dxy_) {
        if(debug_) {
          std::cout << "FAILS abs(dxy) = " << absDxy << " <= " << max_dxy_ << " cut\n";
        }
        continue;
      }
      const double absDz = std::fabs(electron->dB(pat::Electron::PVDZ));
      if(absDz > max_dz_) {
        if(debug_) {
          std::cout << "FAILS abs(dz) = " << absDz << " <= " << max_dz_ << " cut\n";
        }
        continue;
      }
      const double relIso = electron->userFloat("miniIsoAll") / electron->pt();
      if(relIso > max_relIso_) {
        if(debug_) {
          std::cout << "FAILS relIso = " << relIso << " <= " << max_relIso_ << " cut\n";
        }
        continue;
      }
      const double sip3d = std::fabs(electron->dB(pat::Electron::PV3D) / electron->edB(pat::Electron::PV3D));
      if(sip3d > max_sip3d_) {
        if(debug_) {
          std::cout << "FAILS sip3d = " << sip3d << " <= " << max_sip3d_ << " cut\n";
        }
        continue;
      }
      if(electron->gsfTrack().isNull() || electron->gsfTrack()->hitPattern().numberOfLostHits(reco::HitPattern::MISSING_INNER_HITS) > max_nLostHits_) {
        if(debug_) {
          std::cout << "FAILS nLostHits <= " << max_nLostHits_ << " cut\n";
        }
        continue;
      }
      if(apply_conversionVeto_ && ! electron->passConversionVeto()) {
        if(debug_) {
          std::cout << "FAILS conversion veto\n";
        }
        continue;
      }
      if(! electron->userInt("mvaFall17V1noIso_WPL")) {
        if(debug_) {
          std::cout << "FAILS EGamma POG MVA cut\n";
        }
        continue;
      }
      if(apply_offline_e_trigger_cuts_ && electron->pt() > min_pt_trig_) {
        const double max_sigmaEtaEta_trig = min_sigmaEtaEta_trig_ + max_sigmaEtaEta_trig_ * (absEta > binning_absEta_);
        if(electron->full5x5_sigmaIetaIeta() > max_sigmaEtaEta_trig) {
          if(debug_) {
            std::cout << "FAILS sigmaEtaEta = " << electron->full5x5_sigmaIetaIeta() << " <= " << max_sigmaEtaEta_trig << " cut\n";
          }
          continue;
        }
        if(electron->hadronicOverEm() > max_HoE_trig_) {
          if(debug_) {
            std::cout << "FAILS HoE = " << electron->hadronicOverEm() << " <= " << max_HoE_trig_ << " cut\n";
          }
          continue;
        }
        const double OoEminusOoP = (1 - electron->eSuperClusterOverP()) / electron->ecalEnergy();
        if(OoEminusOoP < min_OoEminusOoP_trig_) {
          if(debug_) {
            std::cout << "FAILS OoEminusOoP = " << OoEminusOoP << " >= " << min_OoEminusOoP_trig_ << " cut\n";
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
    desc.add<edm::InputTag>("src_mvaTTH")->setComment("ttH lepton ID MVA input collection for electrons");
    desc.add<std::string>("era")->setComment("run period");
    desc.add<bool>("debug")->setComment("debug flag");
    descriptions.add("PATElectronSelectorFakeable", desc);
  }

private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::View<pat::Electron>> token_;  
  edm::InputTag src_mvaTTH_;
  edm::EDGetTokenT<edm::ValueMap<float>> token_mvaTTH_;

  int era_;
  bool debug_;
  bool apply_offline_e_trigger_cuts_;

  float min_pt_;                ///< lower cut threshold on lepton pT
  float max_absEta_;            ///< upper cut threshold on absolute value of eta
  float max_dxy_;               ///< upper cut threshold on d_{xy}, distance in the transverse plane w.r.t PV
  float max_dz_;                ///< upper cut threshold on d_{z}, distance on the z axis w.r.t PV
  float max_relIso_;            ///< upper cut threshold on relative isolation
  float max_sip3d_;             ///< upper cut threshold on significance of IP
  float binning_absEta_;        ///< eta values separating central, transition and forward region (0.8, 1.479)
  float min_pt_trig_;           ///< lower pT threshold for applying shower shape cuts (to mimic selection applied on trigger level)
  float min_sigmaEtaEta_trig_;  ///< lower cut threshold on second shower moment in eta-direction
  float max_sigmaEtaEta_trig_;  ///< upper cut threshold on second shower moment in eta-direction
  float max_HoE_trig_;          ///< upper cut threshold on ratio of energy deposits in hadronic/electromagnetic section of calorimeter
  float min_OoEminusOoP_trig_;  ///< lower cut threshold on difference between calorimeter energy and track momentum (1/E - 1/P)
  float wp_mvaTTH_;             ///< lepton MVA WP; not used as the cuts that depend on the WP are applied to nearby jet
  bool apply_conversionVeto_;   ///< apply (True) or do not apply (False) conversion veto
  int max_nLostHits_;           ///< upper cut threshold on lost hits in the innermost layer of the tracker (electrons with lost_hits equal to cut threshold pass) 
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(PATElectronSelectorFakeable);
