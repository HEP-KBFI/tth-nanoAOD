import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var

def addJetSubstructureObservables(process, runOnMC):

    #----------------------------------------------------------------------------
    # add anti-kT jets for dR = 1.2 (AK12),
    # following instructions posted by Sal on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1792/1.html)
    from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox
    jetToolbox(process, 'ak12', 'jetSequenceAK12', 'out', PUMethod='Puppi', miniAOD=True, runOnMC=runOnMC, addSoftDrop=True, addSoftDropSubjets=True)
    # CV: use jet energy corrections for AK8 Puppi jets
    process.patJetCorrFactorsAK12PFPuppi.payload = cms.string('AK8PFPuppi')   
    process.patJetCorrFactorsAK12PFPuppiSoftDrop.payload = cms.string('AK8PFPuppi')
    fatJetCollectionAK12 = 'patJetsAK12PFPuppi'
    subJetCollectionAK12 = 'selectedPatJetsAK12PFPuppiSoftDropPacked:SubJets'
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add PF jet ID flags and jet energy corrections for AK12 pat::Jet collection,
    # following what is done for AK8 pat::Jets in https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/jets_cff.py
    process.looseJetIdAK12 = process.looseJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.tightJetIdAK12 = process.tightJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetsAK12WithUserData = process.slimmedJetsAK8WithUserData.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetsAK12WithUserData.userInts.tightId = cms.InputTag("tightJetIdAK8")
    process.jetsAK12WithUserData.userInts.looseId = cms.InputTag("looseJetIdAK8")
    process.jetCorrFactorsAK12 = process.jetCorrFactorsAK8.clone(
        src = cms.InputTag('jetsAK12WithUserData')
    )
    process.updatedJetsAK12 = process.updatedJetsAK8.clone(
        jetSource = cms.InputTag('jetsAK12WithUserData'),
	jetCorrFactorsSource = cms.VInputTag(cms.InputTag('jetCorrFactorsAK12'))
    )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
    # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
    if not hasattr(process, "RandomNumberGeneratorService"):
        process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
    process.RandomNumberGeneratorService.QJetsAdderCA8 = cms.PSet(initialSeed = cms.untracked.uint32(7))
    process.RandomNumberGeneratorService.QJetsAdderAK8 = cms.PSet(initialSeed = cms.untracked.uint32(31))
    process.RandomNumberGeneratorService.QJetsAdderCA15 = cms.PSet(initialSeed = cms.untracked.uint32(76))
    from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
    process.QJetsAdderAK12 = QJetsAdder.clone(
        src = cms.InputTag('updatedJetsAK12'),
        jetRad = cms.double(1.2),
        jetAlgo = cms.string("ak")
    )
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility as userFloats to AK12 pat::Jet collection
    process.extendedFatJetsAK12 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('updatedJetsAK12'),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            ),
            cms.PSet(
                pluginType = cms.string("JetValueMapPlugin"),
                label = cms.string("QjetVolatility"),
                overwrite = cms.bool(False),
                src = cms.InputTag('QJetsAdderAK12')
            )
        )
    )
    process.extendedSubJetsAK12 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag(subJetCollectionAK12),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            )
        )
    )
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility to nanoAOD
    process.fatJetTableAK12 = process.fatJetTable.clone()
    process.fatJetTableAK12.src = cms.InputTag('extendedFatJetsAK12')
    process.fatJetTableAK12.cut = cms.string("pt > 100")
    process.fatJetTableAK12.name = cms.string("FatJetAK12")
    process.fatJetTableAK12.doc = cms.string("ak12 fat jets for boosted analysis")
    process.fatJetTableAK12.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.fatJetTableAK12.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTableAK12.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTableAK12.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTableAK12.variables.QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10)
    process.subJetTableAK12 = process.subJetTable.clone()
    process.subJetTableAK12.src = cms.InputTag('extendedSubJetsAK12')
    process.subJetTableAK12.cut = cms.string("")
    process.subJetTableAK12.name = cms.string("SubJetAK12")
    process.subJetTableAK12.doc = cms.string("ak12 sub-jets for boosted analysis")
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge and pull as userFloats to AK4 pat::Jet collection
    process.extendedJets = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('updatedJets'),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            )
        )
    )
    process.jetSequence.replace(process.updatedJets, process.updatedJets + process.extendedJets)
    process.finalJets.src = cms.InputTag('extendedJets')
    process.jetTable.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.jetTable.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    #----------------------------------------------------------------------------
