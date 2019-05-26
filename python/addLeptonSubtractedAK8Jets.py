import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

def addLeptonSubtractedAK8Jets(process, runOnMC, era, useFakeable, addQJets = False):

    assert(era in [ "2016", "2017", "2018" ])
    suffix = "Fakeable" if useFakeable else "Loose"

    #----------------------------------------------------------------------------
    # produce collections of electrons and muons passing loose or fakeable lepton selection of ttH multilepton+tau analysis (HIG-18-019)
    electronCollectionTTH_str = 'electronCollectionTTH%s' % suffix
    setattr(process, electronCollectionTTH_str,
        cms.EDProducer("PATElectronSelector%s" % suffix,
            src = cms.InputTag("linkedObjects", "electrons"),
            src_mvaTTH = cms.InputTag("electronMVATTH"),
            era = cms.string(era),
            debug = cms.bool(False)
        )
    )
    muonCollectionTTH_str = 'muonCollectionTTH%s' % suffix
    setattr(process, muonCollectionTTH_str,
        cms.EDProducer("PATMuonSelector%s" % suffix,
            src = cms.InputTag("linkedObjects", "muons"),
            src_mvaTTH = cms.InputTag("muonMVATTH"),
            era = cms.string(era),
            debug = cms.bool(False)
        )
    )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to loose or fakeable electrons or muons
    leptonLessPFProducer_str = 'leptonLessPFProducer%s' % suffix
    setattr(process, leptonLessPFProducer_str,
        cms.EDProducer('LeptonLessPFProducer',
            src_pfCands = cms.InputTag("packedPFCandidates"),
            src_electrons = cms.InputTag(electronCollectionTTH_str),
            src_muons = cms.InputTag(muonCollectionTTH_str),
            debug = cms.bool(False)
       )
    )

    # run PUPPI algorithm (arXiv:1407.6013) on cleaned packedPFCandidates collection
    # cf. https://twiki.cern.ch/twiki/bin/view/CMS/JetToolbox#New_PF_Collection
    from CommonTools.PileupAlgos.Puppi_cff import puppi
    leptonLesspuppi_str = 'leptonLesspuppi%s' % suffix
    setattr(process, leptonLesspuppi_str,
        puppi.clone(
            candName = cms.InputTag(leptonLessPFProducer_str),
            vertexName = cms.InputTag("offlineSlimmedPrimaryVertices"),
            useExistingWeights = cms.bool(True)
        )
    )
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

    jetSequenceAK8LS_str = 'jetSequenceAK8LS%s' % suffix
    NoLep_str = 'NoLep%s' % suffix
    jetToolbox(
        proc = process, jetType = 'ak8', jetSequence = jetSequenceAK8LS_str, outputFile = 'out', PUMethod = 'Puppi',
        JETCorrPayload = 'AK8PFPuppi', postFix = NoLep_str, JETCorrLevels = JETCorrLevels, miniAOD = True,
        runOnMC = runOnMC, newPFCollection = True, nameNewPFCollection = leptonLesspuppi_str, addSoftDrop = True,
        addSoftDropSubjets = True, addNsub = True, subJETCorrPayload = 'AK4PFPuppi', subJETCorrLevels = JETCorrLevels,
        bTagDiscriminators = bTagDiscriminators
    )
    # CV: fix ordering of modules in jet sequence
    #    (NjettinessAK8PuppiNoLep needs to be run before selectedPatJetsAK8PFPuppiNoLepSoftDropPacked)
    jetSequenceAK8LS = getattr(process, jetSequenceAK8LS_str)
    jetSequenceAK8LS.remove(getattr(process, 'NjettinessAK8Puppi%s' % NoLep_str))
    jetSequenceAK8LS.replace(
        getattr(process, 'selectedPatJetsAK8PFPuppi%sSoftDropPacked' % NoLep_str),
        getattr(process, 'NjettinessAK8Puppi%s' % NoLep_str) + \
        getattr(process, 'selectedPatJetsAK8PFPuppi%sSoftDropPacked' % NoLep_str)
    )
    # CV: disable discriminators that cannot be computed with miniAOD inputs
    #for moduleName in [ "patJetsAK8LSPFPuppi", "patJetsAK8LSPFPuppiSoftDrop", "patJetsAK8LSPFPuppiSoftDropSubjets" ]:
    #    module = getattr(process, moduleName)
    #    module.discriminatorSources = cms.VInputTag()
    fatJetCollectionAK8LS_str = 'packedPatJetsAK8PFPuppi%sSoftDrop' % NoLep_str
    subJetCollectionAK8LS_str = 'selectedPatJetsAK8PFPuppi%sSoftDropPacked:SubJets' % NoLep_str
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
    looseJetIdAK8LS_str = 'looseJetIdAK8LS%s' % suffix
    setattr(process, looseJetIdAK8LS_str,
        process.looseJetIdAK8.clone(
            src = cms.InputTag(fatJetCollectionAK8LS_str)
        )
    )
    tightJetIdAK8LS_str = 'tightJetIdAK8LS%s' % suffix
    setattr(process, tightJetIdAK8LS_str,
        process.tightJetIdAK8.clone(
            src = cms.InputTag(fatJetCollectionAK8LS_str)
        )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        tightJetIdAK8LS = getattr(process, tightJetIdAK8LS_str)
        modifier.toModify(tightJetIdAK8LS.filterParams, version = "WINTER16")
    tightJetIdLepVetoAK8LS_str = 'tightJetIdLepVetoAK8LS%s' % suffix
    setattr(process, tightJetIdLepVetoAK8LS_str,
        process.tightJetIdLepVetoAK8.clone(
          src = cms.InputTag(fatJetCollectionAK8LS_str)
        )
    )
    
    #----------------------------------------------------------------------------
    if addQJets:
        # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
        # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
        if not hasattr(process, "RandomNumberGeneratorService"):
            process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
        QJetsAdderAK8LS_str = 'QJetsAdderAK8LS%s' % suffix
        setattr(process.RandomNumberGeneratorService, QJetsAdderAK8LS_str, cms.PSet(initialSeed = cms.untracked.uint32(7)))
        from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
        setattr(process, QJetsAdderAK8LS_str,
            QJetsAdder.clone(
                src = cms.InputTag(fatJetCollectionAK8LS_str),
                jetRad = cms.double(0.8),
                jetAlgo = cms.string("AK")
            )
        )
    subStructureAK8_str = "jetsAK8LSsubStructureVars%s" % suffix
    setattr(process, subStructureAK8_str,
        cms.EDProducer("JetSubstructureObservableProducer",
            src = cms.InputTag(fatJetCollectionAK8LS_str),
            kappa = cms.double(1.),
        )
    )
    #----------------------------------------------------------------------------

    jetsAK8LSWithUserData_str = 'jetsAK8LSWithUserData%s' % suffix
    setattr(process, jetsAK8LSWithUserData_str,
        process.updatedJetsAK8WithUserData.clone(
            src = cms.InputTag(fatJetCollectionAK8LS_str),
            userFloats = cms.PSet(
                jetCharge = cms.InputTag("%s:jetCharge" % subStructureAK8_str),
                pull_dEta = cms.InputTag("%s:pullDEta" % subStructureAK8_str),
                pull_dPhi = cms.InputTag("%s:pullDPhi" % subStructureAK8_str),
                pull_dR   = cms.InputTag("%s:pullDR" % subStructureAK8_str),
            ),
            userInts = cms.PSet(
                tightId = cms.InputTag(tightJetIdAK8LS_str),
                tightIdLepVeto = cms.InputTag(tightJetIdLepVetoAK8LS_str),
            )
        )
    )
    if addQJets:
        jetsAK8LSWithUserData = getattr(process, jetsAK8LSWithUserData_str)
        jetsAK8LSWithUserData.userFloats.QjetVolatility = cms.InputTag('%s:QjetsVolatility' % QJetsAdderAK8LS_str)

    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        jetsAK8LSWithUserData = getattr(process, jetsAK8LSWithUserData_str)
        modifier.toModify(jetsAK8LSWithUserData.userInts,
            looseId = cms.InputTag(looseJetIdAK8LS_str),
            tightIdLepVeto = None,
        )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    subStructureSubJetAK8_str = "subJetsAK8LSsubStructureVars%s" % suffix
    setattr(process, subStructureSubJetAK8_str,
        cms.EDProducer("JetSubstructureObservableProducer",
            src = cms.InputTag(subJetCollectionAK8LS_str),
            kappa = cms.double(1.),
        )
    )
    subJetsAK8LSWithUserData_str = 'subJetsAK8LSWithUserData%s' % suffix
    setattr(process, subJetsAK8LSWithUserData_str,
        cms.EDProducer("PATJetUserDataEmbedder",
            src = cms.InputTag(subJetCollectionAK8LS_str),
            userFloats = cms.PSet(
                jetCharge = cms.InputTag("%s:jetCharge" % subStructureSubJetAK8_str),
                pull_dEta = cms.InputTag("%s:pullDEta" % subStructureSubJetAK8_str),
                pull_dPhi = cms.InputTag("%s:pullDPhi" % subStructureSubJetAK8_str),
                pull_dR   = cms.InputTag("%s:pullDR" % subStructureSubJetAK8_str),
            ),
            userInts = cms.PSet(),
        )
    )
    #----------------------------------------------------------------------------
    # add lepton-subtracted AK8 jets to nanoAOD Ntuple
    fatJetAK8LSTable_str = 'fatJetAK8LS%sTable' % suffix # NB! must end with 'Table'
    setattr(process, fatJetAK8LSTable_str,
        process.fatJetTable.clone(
            src = cms.InputTag(jetsAK8LSWithUserData_str),
            cut = cms.string("pt > 80 && abs(eta) < 2.4"),
            name = cms.string("FatJetAK8LS%s" % suffix),
            doc = cms.string("lepton-subtracted ak8 fat jets for boosted analysis"),
            variables = cms.PSet(P4Vars,
                rawFactor = Var("1.-jecFactor('Uncorrected')",float,doc="1 - Factor to get back to raw pT",precision=10),
                jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
                pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
                pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
                pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10),
                msoftdrop = Var("userFloat('ak8PFJetsPuppi%sSoftDropMass')" % NoLep_str,float, doc="Corrected soft drop mass with PUPPI",precision=10),
                subJetIdx1 = Var("?subjets('SoftDrop').size()>0?subjets('SoftDrop').at(0).key():-1", int, doc="index of first subjet"),
                subJetIdx2 = Var("?subjets('SoftDrop').size()>1?subjets('SoftDrop').at(1).key():-1", int, doc="index of second subjet"),
                tau1 = Var("userFloat('NjettinessAK8Puppi%s:tau1')" % NoLep_str,float, doc="Nsubjettiness (1 axis)",precision=10),
                tau2 = Var("userFloat('NjettinessAK8Puppi%s:tau2')" % NoLep_str,float, doc="Nsubjettiness (2 axis)",precision=10),
                tau3 = Var("userFloat('NjettinessAK8Puppi%s:tau3')" % NoLep_str,float, doc="Nsubjettiness (3 axis)",precision=10),
                tau4 = Var("userFloat('NjettinessAK8Puppi%s:tau4')" % NoLep_str,float, doc="Nsubjettiness (4 axis)",precision=10),
                jetId = Var("userInt('tightId')*2+4*userInt('tightIdLepVeto')",int,doc="Jet ID flags bit1 is loose (always false in 2017 since it does not exist), bit2 is tight, bit3 is tightLepVeto"),
                area = Var("jetArea()", float, doc="jet catchment area, for JECs", precision=10),
                btagCMVA = Var("bDiscriminator('pfCombinedMVAV2BJetTags')",float,doc="CMVA V2 btag discriminator",precision=10),
                btagDeepB = Var("bDiscriminator('pfDeepCSVJetTags:probb')+bDiscriminator('pfDeepCSVJetTags:probbb')",float,doc="DeepCSV b+bb tag discriminator",precision=10),
                btagCSVV2 = Var("bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc=" pfCombinedInclusiveSecondaryVertexV2 b-tag discriminator (aka CSVV2)",precision=10),
                btagHbb = Var("bDiscriminator('pfBoostedDoubleSecondaryVertexAK8BJetTags')",float,doc="Higgs to BB tagger discriminator",precision=10),
            )
        )
    )
    if addQJets:
        fatJetAK8LSTable = getattr(process, fatJetAK8LSTable_str)
        fatJetAK8LSTable.variables.QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10)
        print("Adding Qjet volatility to %s" % jetsAK8LSWithUserData_str)
    else:
        print("NOT adding Qjet volatility to %s" % jetsAK8LSWithUserData_str)

    ### Era dependent customization
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        fatJetAK8LSTable = getattr(process, fatJetAK8LSTable_str)
        modifier.toModify(
            fatJetAK8LSTable.variables,
            jetId = Var("userInt('tightId')*2+userInt('looseId')", int, doc="Jet ID flags bit1 is loose, bit2 is tight")
        )

    subJetAK8LSTable_str = 'subJetAK8LS%sTable' % suffix # NB! must end with 'Table'
    setattr(process, subJetAK8LSTable_str,
        process.subJetTable.clone(
            src = cms.InputTag(subJetsAK8LSWithUserData_str),
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
    )
    subJetAK8LSTable = getattr(process, subJetAK8LSTable_str)
    run2_miniAOD_80XLegacy.toModify(subJetAK8LSTable.variables, btagCMVA = None, btagDeepB = None)

    leptonSubtractedJetSequence = cms.Sequence(
        getattr(process, electronCollectionTTH_str) + getattr(process, muonCollectionTTH_str) + \
        getattr(process, leptonLessPFProducer_str) + getattr(process, leptonLesspuppi_str) + \
        getattr(process, jetSequenceAK8LS_str) + getattr(process, tightJetIdAK8LS_str) + \
        getattr(process, tightJetIdLepVetoAK8LS_str) + getattr(process, subStructureAK8_str) + \
        getattr(process, jetsAK8LSWithUserData_str) + getattr(process, subStructureSubJetAK8_str) + \
        getattr(process, subJetsAK8LSWithUserData_str) + getattr(process, fatJetAK8LSTable_str) + \
        getattr(process, subJetAK8LSTable_str)
    )
    if addQJets:
        leptonSubtractedJetSequence.replace(
            getattr(process, jetsAK8LSWithUserData_str),
            getattr(process, QJetsAdderAK8LS_str) + getattr(process, jetsAK8LSWithUserData_str)
        )

    #----------------------------------------------------------------------------

    _leptonSubtractedJetSequence_80X = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_80X.replace(getattr(process, tightJetIdLepVetoAK8LS_str), getattr(process, looseJetIdAK8LS_str))
    run2_miniAOD_80XLegacy.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_80X)

    _leptonSubtractedJetSequence_94X2016 = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_94X2016.replace(getattr(process, tightJetIdLepVetoAK8LS_str), getattr(process, looseJetIdAK8LS_str))
    run2_nanoAOD_94X2016.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_94X2016)

    leptonSubtractedJetSequence_str = 'leptonSubtractedJetSequence%s' % suffix
    setattr(process, leptonSubtractedJetSequence_str, leptonSubtractedJetSequence)
    process.nanoSequence += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceMC += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceFS += getattr(process, leptonSubtractedJetSequence_str)
