
/** \class JetExtendedProducer
 *
 * Produce collection of pat::Jet objects with different observables relevant for jet substructure analyses added as userFloats.
 * The userFloats are computed via plugins inheriting from JetExtendedPluginBase class.
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

#include "DataFormats/Common/interface/View.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/Common/interface/ValueMap.h"
#include "DataFormats/Common/interface/RefToBase.h"

#include "tthAnalysis/NanoAOD/interface/JetExtendedPluginBase.h"
#include "tthAnalysis/NanoAOD/interface/JetValueMapPlugin.h"

class JetExtendedProducer : public edm::stream::EDProducer<>
{
 public:
  JetExtendedProducer(const edm::ParameterSet& cfg)
    : src_(cfg.getParameter<edm::InputTag>("src"))
  {
    token_ = consumes<edm::View<pat::Jet>>(src_);
    edm::VParameterSet cfgPlugins = cfg.getParameter<edm::VParameterSet>("plugins");
    for ( edm::VParameterSet::const_iterator cfgPlugin = cfgPlugins.begin();
	  cfgPlugin != cfgPlugins.end(); ++cfgPlugin ) {
      std::string pluginType = cfgPlugin->getParameter<std::string>("pluginType");
      JetExtendedPluginBase* plugin = JetExtendedPluginFactory::get()->create(pluginType, *cfgPlugin);
      JetValueMapPlugin* plugin_JetValueMap = dynamic_cast<JetValueMapPlugin*>(plugin);
      if ( plugin_JetValueMap ) {
	plugin_JetValueMap->token_ = consumes<edm::ValueMap<float>>(plugin_JetValueMap->src_);
      }
      plugins_.push_back(plugin);
    }
    produces<pat::JetCollection>();
  }
  ~JetExtendedProducer() {}

  void produce(edm::Event& evt, const edm::EventSetup& es)
  {
    edm::Handle<edm::View<pat::Jet>> inputJets;
    evt.getByToken(token_, inputJets);

    std::unique_ptr<pat::JetCollection> outputJets(new pat::JetCollection());

    size_t numJets = inputJets->size();
    for ( size_t idxJet = 0; idxJet < numJets; ++idxJet ) {
      edm::RefToBase<reco::Jet> inputJetRef(inputJets->refAt(idxJet));
      edm::RefToBase<pat::Jet> inputPatJetRef(inputJetRef.castTo<pat::JetRef>());
      pat::Jet outputJet(inputPatJetRef);
      for ( std::vector<JetExtendedPluginBase*>::const_iterator plugin = plugins_.begin();
	    plugin != plugins_.end(); ++plugin ) {
	JetValueMapPlugin* plugin_JetValueMap = dynamic_cast<JetValueMapPlugin*>(*plugin);
	if ( plugin_JetValueMap ) {
	  edm::Handle<edm::ValueMap<float>> valueMap;
	  evt.getByToken(plugin_JetValueMap->token_, valueMap);
	  double value = (*valueMap)[inputJetRef];
	  (*plugin_JetValueMap)(outputJet, value);
	} else {
	  (**plugin)(outputJet);
	}
      }
      outputJets->push_back(outputJet);
    }

    evt.put(std::move(outputJets));
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions)
  {
    edm::ParameterSetDescription desc;
    desc.setComment("PAT jet producer module");
    desc.add<edm::InputTag>("src")->setComment("jet input collection");
    edm::ParameterSetDescription desc_plugins;
    desc_plugins.add<std::string>("pluginType")->setComment("C++ class type of plugin");
    desc_plugins.add<std::string>("label")->setComment("Name of userFloat used to store value computed by plugin");
    desc_plugins.add<bool>("overwrite")->setComment("Flag to enable/disable overwriting of userFloat in case a userFloat of given name already exists in the jet input collection");
    desc_plugins.addOptional<double>("kappa")->setComment("Exponent used to compute jet charge (specific to JetChargePlugin)");
    desc_plugins.addOptional<edm::InputTag>("src")->setComment("Name of ValueMap (specific to JetValueMapPlugin)"); 
    desc.addVPSet("plugins", desc_plugins)->setComment("collections of plugins adding observables as userFloats");
    descriptions.add("JetExtendedProducer", desc);
  }

 private:
  edm::InputTag src_;
  edm::EDGetTokenT<edm::View<pat::Jet>> token_;
  std::vector<JetExtendedPluginBase*> plugins_;
};

#include "FWCore/Framework/interface/MakerMacros.h"

DEFINE_FWK_MODULE(JetExtendedProducer);