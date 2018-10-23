import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy

def addLeptonSubtractedAK8Jets(process, runOnMC):

    leptonSubtractedJetSequence = cms.Sequence()

    #----------------------------------------------------------------------------
    # produce collections of electrons and muons passing fakeable lepton selection of ttH multilepton+tau analysis (HIG-18-019)
    process.fakeableElectronsTTH = cms.EDProducer("PATElectronSelectorFakeable",
        src = cms.InputTag("linkedObjects", "electrons"),
        src_mvaTTH = cms.InputTag("electronMVATTH"),
        era = cms.string("2017"),
        debug = cms.bool(False)
    )
    leptonSubtractedJetSequence += process.fakeableElectronsTTH

    process.fakeableMuonsTTH = cms.EDProducer("PATMuonSelectorFakeable",
        src = cms.InputTag("linkedObjects", "muons"),
        src_mvaTTH = cms.InputTag("muonMVATTH"),
        era = cms.string("2017"),
        debug = cms.bool(False)
    )
    leptonSubtractedJetSequence += process.fakeableMuonsTTH
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to fakeable electrons or muons
    process.leptonLessPFProducer = cms.EDProducer('LeptonLessPFProducer',
        src_pfCands = cms.InputTag("packedPFCandidates"),
        src_electrons = cms.InputTag("fakeableElectronsTTH"),
        src_muons = cms.InputTag("fakeableMuonsTTH"),
        debug = cms.bool(True)
    )
    leptonSubtractedJetSequence += process.leptonLessPFProducer

    # run PUPPI algorithm (arXiv:1407.6013) on cleaned packedPFCandidates collection
    # cf. https://twiki.cern.ch/twiki/bin/view/CMS/JetToolbox#New_PF_Collection
    from CommonTools.PileupAlgos.Puppi_cff import puppi
    process.leptonLesspuppi = puppi.clone(
        candName = cms.InputTag("leptonLessPFProducer"),
        vertexName = cms.InputTag("offlineSlimmedPrimaryVertices"),
        useExistingWeights = cms.bool(True)
    )
    leptonSubtractedJetSequence += process.leptonLesspuppi
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # reconstruct lepton-subtracted AK8 jets
    from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox
    bTagDiscriminators = [ 'pfCombinedInclusiveSecondaryVertexV2BJetTags', 'pfBoostedDoubleSecondaryVertexAK8BJetTags' ]
    JETCorrLevels = [ 'L1FastJet', 'L2Relative', 'L3Absolute' ]
    if not runOnMC:
        JETCorrLevels.append('L2L3Residual')  
    jetToolbox(process, 'ak8', 'jetSequenceAK8LS', 'out', PUMethod='Puppi', JETCorrPayload='AK8PFPuppi', postFix='NoLep', JETCorrLevels=JETCorrLevels, miniAOD=True, runOnMC=runOnMC,
               newPFCollection=True, nameNewPFCollection='leptonLesspuppi', addSoftDrop=True, addSoftDropSubjets=True, addNsub=True,
               subJETCorrPayload='AK4PFPuppi',subJETCorrLevels=JETCorrLevels, bTagDiscriminators=bTagDiscriminators)    
    leptonSubtractedJetSequence += process.jetSequenceAK8LS
    # CV: disable discriminators that cannot be computed with miniAOD inputs
    #for moduleName in [ "patJetsAK8LSPFPuppi", "patJetsAK8LSPFPuppiSoftDrop", "patJetsAK8LSPFPuppiSoftDropSubjets" ]:
    #    module = getattr(process, moduleName)
    #    module.discriminatorSources = cms.VInputTag()
    fatJetCollectionAK8LS = 'packedPatJetsAK8PFPuppiNoLepSoftDrop'
    subJetCollectionAK8LS = 'selectedPatJetsAK8PFPuppiNoLepSoftDropPacked:SubJets'
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # CV: add 'patJetPartons' module to 'genParticleSequence' (which runs at beginning of event processing),
    #     to avoid run-time exception of type:
    #
    #       ----- Begin Fatal Exception 22-Feb-2018 10:16:02 EET-----------------------
    #       An exception of category 'ScheduleExecutionFailure' occurred while
    #          [0] Calling beginJob
    #       Exception Message:
    #       Unrunnable schedule
    #       Module run order problem found:
    #       ...
    #        Running in the threaded framework would lead to indeterminate results.
    #        Please change order of modules in mentioned Path(s) to avoid inconsistent module ordering.
    #       ----- End Fatal Exception -------------------------------------------------
    if hasattr(process, "patJetPartons") and hasattr(process, "genParticleSequence") and runOnMC:
        process.genParticleSequence += process.patJetPartons
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # add PF jet ID flags and jet energy corrections for AK8 pat::Jet collection,
    # following what is done for lepton-subtracted AK8 pat::Jets in https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/jets_cff.py
    process.looseJetIdAK8LS = process.looseJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK8LS)
    )
    process.tightJetIdAK8LS = process.tightJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK8LS)
    )
    process.tightJetIdLepVetoAK8LS = process.tightJetIdLepVetoAK8.clone(
        src = cms.InputTag(fatJetCollectionAK8LS)
    )
    leptonSubtractedJetSequence += process.tightJetIdAK8LS
    leptonSubtractedJetSequence += process.tightJetIdLepVetoAK8LS
    process.jetsAK8LSWithUserData = process.slimmedJetsAK8WithUserData.clone(
        src = cms.InputTag(fatJetCollectionAK8LS),
        userInts = cms.PSet(
            tightId = cms.InputTag("tightJetIdAK8LS"),
            tightIdLepVeto = cms.InputTag("tightJetIdLepVetoAK8LS"),
        )
    )
    run2_miniAOD_80XLegacy.toModify(process.jetsAK8LSWithUserData.userInts,
        looseId = cms.InputTag("looseJetIdAK8LS"),
        tightIdLepVeto = None,
    )
    leptonSubtractedJetSequence += process.jetsAK8LSWithUserData
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
    # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
    if not hasattr(process, "RandomNumberGeneratorService"):
        process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
    process.RandomNumberGeneratorService.QJetsAdderAK8LS = cms.PSet(initialSeed = cms.untracked.uint32(7))
    from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
    process.QJetsAdderAK8LS = QJetsAdder.clone(
        src = cms.InputTag('jetsAK8LSWithUserData'),
        jetRad = cms.double(0.8),
        jetAlgo = cms.string("AK")
    )
    leptonSubtractedJetSequence += process.QJetsAdderAK8LS
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility to AK8 pat::Jet collection
    process.extendedFatJetsAK8LS = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('jetsAK8LSWithUserData'),
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
                src = cms.InputTag('QJetsAdderAK8LS:QjetsVolatility')
            )
        )
    )
    leptonSubtractedJetSequence += process.extendedFatJetsAK8LS
    process.extendedSubJetsAK8LS = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag(subJetCollectionAK8LS),
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
    leptonSubtractedJetSequence += process.extendedSubJetsAK8LS
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add lepton-subtracted AK8 jets to nanoAOD Ntuple
    process.fatJetTableAK8LS = process.fatJetTable.clone(
        src = cms.InputTag('extendedFatJetsAK8LS'),
        cut = cms.string("pt > 80 && abs(eta) < 2.4"),
        name = cms.string("FatJetAK8LS"),
        doc = cms.string("lepton-subtracted ak8 fat jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10),
            QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10),
            msoftdrop = Var("userFloat('ak12PFJetsPuppiSoftDropMass')",float, doc="Corrected soft drop mass with PUPPI",precision=10),
            subJetIdx1 = Var("?subjets('SoftDrop').size()>0?subjets('SoftDrop').at(0).key():-1", int, doc="index of first subjet"),
            subJetIdx2 = Var("?subjets('SoftDrop').size()>1?subjets('SoftDrop').at(1).key():-1", int, doc="index of second subjet"),
            tau1 = Var("userFloat('NjettinessAK12Puppi:tau1')",float, doc="Nsubjettiness (1 axis)",precision=10),
            tau2 = Var("userFloat('NjettinessAK12Puppi:tau2')",float, doc="Nsubjettiness (2 axis)",precision=10),
            tau3 = Var("userFloat('NjettinessAK12Puppi:tau3')",float, doc="Nsubjettiness (3 axis)",precision=10),
            tau4 = Var("userFloat('NjettinessAK12Puppi:tau4')",float, doc="Nsubjettiness (4 axis)",precision=10)
        )
    )
    leptonSubtractedJetSequence += process.fatJetTableAK8LS
        
    process.subJetTableAK8LS = process.subJetTable.clone(
        src = cms.InputTag('extendedSubJetsAK8LS'),
        cut = cms.string(""),
        name = cms.string("SubJetAK8LS"),
        doc = cms.string("lepton-subtracted ak8  sub-jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
        )
    )
    leptonSubtractedJetSequence += process.subJetTableAK8LS
    #----------------------------------------------------------------------------
