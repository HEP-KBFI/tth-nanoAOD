import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

def addLeptonSubtractedAK8Jets(process, runOnMC, era, useFakeable = True):

    assert(era in [ "2016", "2017", "2018" ])

    process.leptonSubtractedJetSequence = cms.Sequence()

    #----------------------------------------------------------------------------
    # produce collections of electrons and muons passing loose or fakeable lepton selection of ttH multilepton+tau analysis (HIG-18-019)
    process.electronCollectionTTH = cms.EDProducer("PATElectronSelectorFakeable" if useFakeable else "PATElectronSelectorLoose",
        src = cms.InputTag("linkedObjects", "electrons"),
        src_mvaTTH = cms.InputTag("electronMVATTH"),
        era = cms.string(era),
        debug = cms.bool(False)
    )
    process.leptonSubtractedJetSequence += process.electronCollectionTTH

    process.muonCollectionTTH = cms.EDProducer("PATMuonSelectorFakeable" if useFakeable else "PATMuonSelectorLoose",
        src = cms.InputTag("linkedObjects", "muons"),
        src_mvaTTH = cms.InputTag("muonMVATTH"),
        era = cms.string(era),
        debug = cms.bool(False)
    )
    process.leptonSubtractedJetSequence += process.muonCollectionTTH
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to loose or fakeable electrons or muons
    process.leptonLessPFProducer = cms.EDProducer('LeptonLessPFProducer',
        src_pfCands = cms.InputTag("packedPFCandidates"),
        src_electrons = cms.InputTag("electronCollectionTTH"),
        src_muons = cms.InputTag("muonCollectionTTH"),
        debug = cms.bool(False)
    )
    process.leptonSubtractedJetSequence += process.leptonLessPFProducer

    # run PUPPI algorithm (arXiv:1407.6013) on cleaned packedPFCandidates collection
    # cf. https://twiki.cern.ch/twiki/bin/view/CMS/JetToolbox#New_PF_Collection
    from CommonTools.PileupAlgos.Puppi_cff import puppi
    process.leptonLesspuppi = puppi.clone(
        candName = cms.InputTag("leptonLessPFProducer"),
        vertexName = cms.InputTag("offlineSlimmedPrimaryVertices"),
        useExistingWeights = cms.bool(True)
    )
    process.leptonSubtractedJetSequence += process.leptonLesspuppi
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # reconstruct lepton-subtracted AK8 jets
    from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox
    bTagDiscriminators = [
        'pfCombinedInclusiveSecondaryVertexV2BJetTags', 'pfBoostedDoubleSecondaryVertexAK8BJetTags',
        'pfCombinedMVAV2BJetTags', 'pfDeepCSVJetTags:probb', 'pfDeepCSVJetTags:probbb'
    ]
    JETCorrLevels = [ 'L1FastJet', 'L2Relative', 'L3Absolute' ]
    if not runOnMC:
        JETCorrLevels.append('L2L3Residual')

    #TODO when running with run2_miniAOD_80XLegacy, JETCorrPayload = 'AK8PFchs' !
    jetToolbox(
        proc = process, jetType = 'ak8', jetSequence = 'jetSequenceAK8LS', outputFile = 'out', PUMethod = 'Puppi',
        JETCorrPayload = 'AK8PFPuppi', postFix = 'NoLep', JETCorrLevels = JETCorrLevels, miniAOD = True,
        runOnMC = runOnMC, newPFCollection = True, nameNewPFCollection = 'leptonLesspuppi', addSoftDrop = True,
        addSoftDropSubjets = True, addNsub = True, subJETCorrPayload = 'AK4PFPuppi', subJETCorrLevels = JETCorrLevels,
        bTagDiscriminators = bTagDiscriminators
    )
    # CV: fix ordering of modules in jet sequence
    #    (NjettinessAK8PuppiNoLep needs to be run before selectedPatJetsAK8PFPuppiNoLepSoftDropPacked)
    process.jetSequenceAK8LS.remove(process.NjettinessAK8PuppiNoLep)
    process.jetSequenceAK8LS.replace(
        process.selectedPatJetsAK8PFPuppiNoLepSoftDropPacked,
        process.NjettinessAK8PuppiNoLep + process.selectedPatJetsAK8PFPuppiNoLepSoftDropPacked
    )
    process.leptonSubtractedJetSequence += process.jetSequenceAK8LS
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
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(process.tightJetIdAK8LS.filterParams, version = "WINTER16")
    process.tightJetIdLepVetoAK8LS = process.tightJetIdLepVetoAK8.clone(
        src = cms.InputTag(fatJetCollectionAK8LS)
    )
    process.leptonSubtractedJetSequence += process.tightJetIdAK8LS
    process.leptonSubtractedJetSequence += process.tightJetIdLepVetoAK8LS

    process.jetsAK8LSWithUserData = process.slimmedJetsAK8WithUserData.clone(
        src = cms.InputTag(fatJetCollectionAK8LS),
        userInts = cms.PSet(
            tightId = cms.InputTag("tightJetIdAK8LS"),
            tightIdLepVeto = cms.InputTag("tightJetIdLepVetoAK8LS"),
        )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(process.jetsAK8LSWithUserData.userInts,
            looseId = cms.InputTag("looseJetIdAK8LS"),
            tightIdLepVeto = None,
        )
    process.leptonSubtractedJetSequence += process.jetsAK8LSWithUserData
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
    process.leptonSubtractedJetSequence += process.QJetsAdderAK8LS
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
    process.leptonSubtractedJetSequence += process.extendedFatJetsAK8LS
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
    process.leptonSubtractedJetSequence += process.extendedSubJetsAK8LS
    #----------------------------------------------------------------------------

    suffix = "" if useFakeable else "_loose"

    #----------------------------------------------------------------------------
    # add lepton-subtracted AK8 jets to nanoAOD Ntuple
    process.fatJetAK8LSTable = process.fatJetTable.clone(
        src = cms.InputTag('extendedFatJetsAK8LS'),
        cut = cms.string("pt > 80 && abs(eta) < 2.4"),
        name = cms.string("FatJetAK8LS%s" % suffix),
        doc = cms.string("lepton-subtracted ak8 fat jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10),
            QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10),
            msoftdrop = Var("userFloat('ak8PFJetsPuppiNoLepSoftDropMass')",float, doc="Corrected soft drop mass with PUPPI",precision=10),
            subJetIdx1 = Var("?subjets('SoftDrop').size()>0?subjets('SoftDrop').at(0).key():-1", int, doc="index of first subjet"),
            subJetIdx2 = Var("?subjets('SoftDrop').size()>1?subjets('SoftDrop').at(1).key():-1", int, doc="index of second subjet"),
            tau1 = Var("userFloat('NjettinessAK8PuppiNoLep:tau1')",float, doc="Nsubjettiness (1 axis)",precision=10),
            tau2 = Var("userFloat('NjettinessAK8PuppiNoLep:tau2')",float, doc="Nsubjettiness (2 axis)",precision=10),
            tau3 = Var("userFloat('NjettinessAK8PuppiNoLep:tau3')",float, doc="Nsubjettiness (3 axis)",precision=10),
            tau4 = Var("userFloat('NjettinessAK8PuppiNoLep:tau4')",float, doc="Nsubjettiness (4 axis)",precision=10),
            jetId = Var("userInt('tightId')*2+4*userInt('tightIdLepVeto')",int,doc="Jet ID flags bit1 is loose (always false in 2017 since it does not exist), bit2 is tight, bit3 is tightLepVeto"),
            area = Var("jetArea()", float, doc="jet catchment area, for JECs", precision=10),
            btagCMVA = Var("bDiscriminator('pfCombinedMVAV2BJetTags')",float,doc="CMVA V2 btag discriminator",precision=10),
            btagDeepB = Var("bDiscriminator('pfDeepCSVJetTags:probb')+bDiscriminator('pfDeepCSVJetTags:probbb')",float,doc="DeepCSV b+bb tag discriminator",precision=10),
            btagCSVV2 = Var("bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc=" pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)",precision=10),
            btagHbb = Var("bDiscriminator('pfBoostedDoubleSecondaryVertexAK8BJetTags')",float,doc="Higgs to BB tagger discriminator",precision=10),
        )
    )
    process.leptonSubtractedJetSequence += process.fatJetAK8LSTable

    ### Era dependent customization
    run2_miniAOD_80XLegacy.toModify( process.fatJetAK8LSTable.variables, msoftdrop_chs = Var("userFloat('ak8PFJetsCHSSoftDropMass')",float, doc="Legacy uncorrected soft drop mass with CHS",precision=10))
    run2_miniAOD_80XLegacy.toModify( process.fatJetAK8LSTable.variables.tau1, expr = cms.string("userFloat(\'ak8PFJetsPuppiValueMap:NjettinessAK8PuppiTau1\')"),)
    run2_miniAOD_80XLegacy.toModify( process.fatJetAK8LSTable.variables.tau2, expr = cms.string("userFloat(\'ak8PFJetsPuppiValueMap:NjettinessAK8PuppiTau2\')"),)
    run2_miniAOD_80XLegacy.toModify( process.fatJetAK8LSTable.variables.tau3, expr = cms.string("userFloat(\'ak8PFJetsPuppiValueMap:NjettinessAK8PuppiTau3\')"),)
    run2_miniAOD_80XLegacy.toModify( process.fatJetAK8LSTable.variables, tau4 = None)
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(
            process.fatJetAK8LSTable.variables,
            jetId = Var("userInt('tightId')*2+userInt('looseId')", int, doc="Jet ID flags bit1 is loose, bit2 is tight")
        )

    process.subJetAK8LSTable = process.subJetTable.clone(
        src = cms.InputTag('extendedSubJetsAK8LS'),
        cut = cms.string(""),
        name = cms.string("SubJetAK8LS%s" % suffix),
        doc = cms.string("lepton-subtracted ak8  sub-jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            btagCMVA = Var("bDiscriminator('pfCombinedMVAV2BJetTags')",float,doc="CMVA V2 btag discriminator",precision=10),
            btagDeepB = Var("bDiscriminator('pfDeepCSVJetTags:probb')+bDiscriminator('pfDeepCSVJetTags:probbb')",float,doc="DeepCSV b+bb tag discriminator",precision=10),
            btagCSVV2 = Var("bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc=" pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)",precision=10),
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10),
        )
    )
    run2_miniAOD_80XLegacy.toModify(process.subJetAK8LSTable.variables, btagCMVA = None, btagDeepB = None)
    process.leptonSubtractedJetSequence += process.subJetAK8LSTable
    #----------------------------------------------------------------------------

    _leptonSubtractedJetSequence_80X = process.leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_80X.replace(process.tightJetIdLepVetoAK8LS, process.looseJetIdAK8LS)
    run2_miniAOD_80XLegacy.toReplaceWith(process.leptonSubtractedJetSequence, _leptonSubtractedJetSequence_80X)

    _leptonSubtractedJetSequence_94X2016 = process.leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_94X2016.replace(process.tightJetIdLepVetoAK8LS, process.looseJetIdAK8LS)
    run2_nanoAOD_94X2016.toReplaceWith(process.leptonSubtractedJetSequence, _leptonSubtractedJetSequence_94X2016)

    process.nanoSequence += process.leptonSubtractedJetSequence
    process.nanoSequenceMC += process.leptonSubtractedJetSequence
