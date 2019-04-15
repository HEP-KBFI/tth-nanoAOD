// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/global/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "DataFormats/PatCandidates/interface/Jet.h"

class HTTBtagMatchProducer : public edm::global::EDProducer<> {
    public:
        explicit HTTBtagMatchProducer(const edm::ParameterSet &iConfig) :
            patjet_(consumes<std::vector<pat::Jet>>(iConfig.getParameter<edm::InputTag>("patsubjets"))),
            pfjet_(consumes<edm::View<reco::Jet> >(iConfig.getParameter<edm::InputTag>( "jetSource" )))
        {

            produces<std::vector<pat::Jet> >();
        }

        ~HTTBtagMatchProducer() override {};

        static void fillDescriptions(edm::ConfigurationDescriptions & descriptions) {
            edm::ParameterSetDescription desc;
            desc.add<edm::InputTag>("jetSource", edm::InputTag("no default"))->setComment("input collection");
            desc.add<edm::InputTag>("patsubjets")->setComment("patjet subjet collection");
            descriptions.add("correspondancetable", desc);
        }

    private:
        void produce(edm::StreamID, edm::Event&, edm::EventSetup const&) const override ;

        std::string name_;
        edm::EDGetTokenT<std::vector<pat::Jet>> patjet_;
        edm::EDGetTokenT<edm::View<reco::Jet> > pfjet_;

};

// ------------ method called to produce the data  ------------
void
HTTBtagMatchProducer::produce(edm::StreamID, edm::Event& iEvent, const edm::EventSetup& iSetup) const 
{

    edm::Handle<std::vector<pat::Jet>> patjets;
    iEvent.getByToken(patjet_, patjets);
    edm::Handle<edm::View<reco::Jet>> pfjets;
    iEvent.getByToken(pfjet_, pfjets);

    auto patJets = std::make_unique<std::vector<pat::Jet>>();

   

  for (edm::View<reco::Jet>::const_iterator jet = pfjets->begin(); jet != pfjets->end(); jet++) {
    unsigned int idx = jet - pfjets->begin();
    edm::Ptr<reco::Candidate> jetPtr = pfjets->ptrAt(idx);

    for (unsigned int ib = 0; ib<patjets->size(); ib++) {
      const pat::Jet & j = (*patjets)[ib];
      const edm::Ptr<reco::Candidate>& subjetOrigRef = j.originalObjectRef();

          if (subjetOrigRef == jetPtr) {
            patJets->push_back(j);
          }
      }

    }

    iEvent.put(std::move(patJets));
}



#include "FWCore/Framework/interface/MakerMacros.h"
//define this as a plug-in
DEFINE_FWK_MODULE(HTTBtagMatchProducer);
