import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, ExtVar, P4Vars
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

from RecoJets.JetProducers.PileupJetID_cfi import pileupJetId
from RecoJets.JetProducers.ak4GenJets_cfi import ak4GenJets

from tthAnalysis.NanoAOD.addLeptonSubtractedPFCands import addLeptonSubtractedPFCands, \
                                                           LEPTONLESSGENPARTICLEPRODUCER_STR
from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox

def addLeptonSubtractedAK4Jets(process, runOnMC, era, useFakeable):

    assert(era in [ "2016", "2017", "2018" ])
    suffix = "Fakeable" if useFakeable else "Loose"

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to loose or fakeable electrons or muons
    ( leptonSubtractedPFCandsSequence, leptonLessPU_str ) = addLeptonSubtractedPFCands(process, era, useFakeable, 'chs', runOnMC)
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # reconstruct lepton-subtracted AK4 jets
    bTagDiscriminators = [
        'pfCombinedInclusiveSecondaryVertexV2BJetTags', 
        'pfCombinedMVAV2BJetTags',
    ]
    JETCorrLevels = [ 'L1FastJet', 'L2Relative', 'L3Absolute' ]
    if not runOnMC:
        JETCorrLevels.append('L2L3Residual')

    jetSequenceAK4LS_str = 'jetSequenceAK4LS%s' % suffix
    NoLep_str = 'NoLep%s' % suffix
    jetToolbox(
        proc = process, jetType = 'ak4', jetSequence = jetSequenceAK4LS_str, outputFile = 'out', PUMethod = 'CHS',
        JETCorrPayload = 'AK4PFchs', postFix = NoLep_str, JETCorrLevels = JETCorrLevels, miniAOD = True,
        runOnMC = runOnMC, newPFCollection = True, nameNewPFCollection = leptonLessPU_str,
        bTagDiscriminators = bTagDiscriminators,
    )
    slimmedJetCollectionAK4LS_str = 'selectedPatJetsAK4PFCHS%s' % NoLep_str

    bTagDiscriminators_ = [
        'pfDeepCSVJetTags:probb', 'pfDeepCSVJetTags:probbb', 'pfDeepCSVJetTags:probc', 'pfDeepFlavourJetTags:probb',
        'pfDeepFlavourJetTags:probbb', 'pfDeepFlavourJetTags:problepb', 'pfDeepFlavourJetTags:probc',
    ]
    deepInfoSuffix = 'PlusDeepInfo%s' % NoLep_str
    updateJetCollection(
        process,
        jetSource = cms.InputTag(slimmedJetCollectionAK4LS_str),
        jetCorrections = ('AK4PFchs', cms.vstring(JETCorrLevels), 'None'),
        btagDiscriminators = bTagDiscriminators_,
        postfix = deepInfoSuffix,
    )
    jetCollectionAK4LS_str = "selectedUpdatedPatJets%s" % deepInfoSuffix
    getattr(process, jetCollectionAK4LS_str).cut = cms.string('pt > 15')

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
    # add PF jet ID flags and jet energy corrections for AK4 pat::Jet collection,
    # following what is done for non-lepton-subtracted AK4 pat::Jets in https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/jets_cff.py
    looseJetIdAK4LS_str = 'looseJetIdAK4LS%s' % suffix
    setattr(process, looseJetIdAK4LS_str,
        process.looseJetId.clone(
            src = cms.InputTag(jetCollectionAK4LS_str)
        )
    )
    tightJetIdAK4LS_str = 'tightJetIdAK4LS%s' % suffix
    setattr(process, tightJetIdAK4LS_str,
        process.tightJetId.clone(
            src = cms.InputTag(jetCollectionAK4LS_str)
        )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        tightJetIdAK4LS = getattr(process, tightJetIdAK4LS_str)
        modifier.toModify(tightJetIdAK4LS.filterParams, version = "WINTER16")
    tightJetIdLepVetoAK4LS_str = 'tightJetIdLepVetoAK4LS%s' % suffix
    setattr(process, tightJetIdLepVetoAK4LS_str,
        process.tightJetIdLepVeto.clone(
          src = cms.InputTag(jetCollectionAK4LS_str)
        )
    )

    #----------------------------------------------------------------------------

    bJetVars_str = 'bJetVarsAK4LS%s' % suffix
    setattr(process, bJetVars_str,
        process.bJetVars.clone(
            src = cms.InputTag(jetCollectionAK4LS_str)
        )
    )

    qgtagger_str = 'qgtaggerAK4LS%s' % suffix
    setattr(process, qgtagger_str,
        process.qgtagger.clone(
            srcJets = cms.InputTag(jetCollectionAK4LS_str)
        )
    )

    # ----------------------------------------------------------------------------

    jetSubStructureVars_str = 'jetSubStructureVars%s' % NoLep_str
    setattr(process, jetSubStructureVars_str,
        cms.EDProducer("JetSubstructureObservableProducer",
            src = cms.InputTag(jetCollectionAK4LS_str),
            kappa = cms.double(1.),
        )
    )

    # ----------------------------------------------------------------------------

    pileupJetId_str = 'pileupJetId%s' % NoLep_str
    setattr(process, pileupJetId_str,
        pileupJetId.clone(
            jets = cms.InputTag(jetCollectionAK4LS_str),
            inputIsCorrected = True,
            applyJec = False,
            vertexes = "offlineSlimmedPrimaryVertices",
        )
    )

    # ----------------------------------------------------------------------------

    jetsAK4LSWithUserData_str = 'jetsAK4LSWithUserData%s' % suffix
    setattr(process, jetsAK4LSWithUserData_str,
        process.updatedJetsWithUserData.clone(
            src = cms.InputTag(jetCollectionAK4LS_str),
            userFloats = cms.PSet(
                leadTrackPt = cms.InputTag("%s:leadTrackPt" % bJetVars_str),
                leptonPtRel = cms.InputTag("%s:leptonPtRel" % bJetVars_str),
                leptonPtRatio = cms.InputTag("%s:leptonPtRatio" % bJetVars_str),
                leptonPtRelInv = cms.InputTag("%s:leptonPtRelInv" % bJetVars_str),
                leptonPtRelv0 = cms.InputTag("%s:leptonPtRelv0" % bJetVars_str),
                leptonPtRatiov0 = cms.InputTag("%s:leptonPtRatiov0" % bJetVars_str),
                leptonPtRelInvv0 = cms.InputTag("%s:leptonPtRelInvv0" % bJetVars_str),
                leptonDeltaR = cms.InputTag("%s:leptonDeltaR" % bJetVars_str),
                leptonPt = cms.InputTag("%s:leptonPt" % bJetVars_str),
                vtxPt = cms.InputTag("%s:vtxPt" % bJetVars_str),
                vtxMass = cms.InputTag("%s:vtxMass" % bJetVars_str),
                vtx3dL = cms.InputTag("%s:vtx3dL" % bJetVars_str),
                vtx3deL = cms.InputTag("%s:vtx3deL" % bJetVars_str),
                ptD = cms.InputTag("%s:ptD" % bJetVars_str),
                genPtwNu = cms.InputTag("%s:genPtwNu" % bJetVars_str),
                qgl = cms.InputTag("%s:qgLikelihood" % qgtagger_str),
                jetCharge = cms.InputTag("%s:jetCharge" % jetSubStructureVars_str),
                pull_dEta = cms.InputTag("%s:pullDEta" % jetSubStructureVars_str),
                pull_dPhi = cms.InputTag("%s:pullDPhi" % jetSubStructureVars_str),
                pull_dR = cms.InputTag("%s:pullDR" % jetSubStructureVars_str),
                puIdDisc = cms.InputTag("%s:fullDiscriminant" % pileupJetId_str),
            ),
            userInts = cms.PSet(
                tightId = cms.InputTag(tightJetIdAK4LS_str),
                tightIdLepVeto = cms.InputTag(tightJetIdLepVetoAK4LS_str),
                vtxNtrk = cms.InputTag("%s:vtxNtrk" % bJetVars_str),
                leptonPdgId = cms.InputTag("%s:leptonPdgId" % bJetVars_str),
                puId = cms.InputTag("%s:fullId" % pileupJetId_str),
            )
        )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(getattr(process, jetsAK4LSWithUserData_str).userInts,
            looseId = cms.InputTag("looseJetId"),
        )
    #----------------------------------------------------------------------------

    bjetNN_str = 'bjetNN%s' % NoLep_str
    setattr(process, bjetNN_str,
        process.bjetNN.clone(
            src = cms.InputTag(jetsAK4LSWithUserData_str),
        )
    )

    #----------------------------------------------------------------------------

    # add lepton-subtracted AK4 jets to nanoAOD Ntuple
    jetAK4LSTable_str = 'jetAK4LS%sTable' % suffix # NB! must end with 'Table'
    setattr(process, jetAK4LSTable_str,
        process.jetTable.clone(
            src = cms.InputTag(jetsAK4LSWithUserData_str),
            name = cms.string("JetAK4LS%s" % suffix),
            doc = cms.string("lepton-subtracted ak4 jets"),
            externalVariables = cms.PSet(
                bRegCorr = ExtVar(cms.InputTag("%s:corr" % bjetNN_str),float, doc="pt correction for b-jet energy regression",precision=12),
                bRegRes = ExtVar(cms.InputTag("%s:res" % bjetNN_str),float, doc="res on pt corrected with b-jet regression",precision=8),
            )
        )
    )
    getattr(process, jetAK4LSTable_str).variables.puId = Var("userInt('puId')",int,doc="Pilup ID flags")
    getattr(process, jetAK4LSTable_str).variables.puIdDisc = Var("userFloat('puIdDisc')",float,doc="Pilup ID discriminant")

    if runOnMC:
        getattr(process, jetAK4LSTable_str).variables.partonFlavour = Var("partonFlavour()", int, doc="flavour from parton matching")
        getattr(process, jetAK4LSTable_str).variables.hadronFlavour = Var("hadronFlavour()", int, doc="flavour from hadron ghost clustering")
        getattr(process, jetAK4LSTable_str).variables.genJetIdx = Var("?genJetFwdRef().backRef().isNonnull()?genJetFwdRef().backRef().key():-1", int, doc="index of matched gen jet")

        #----------------------------------------------------------------------------
        # produce lepton-subtracted generator-level jets
        genjetAK4LS_str = 'genJetAK4LS'
        if not hasattr(process, genjetAK4LS_str):
            setattr(process, genjetAK4LS_str,
                ak4GenJets.clone(
                    src = cms.InputTag(LEPTONLESSGENPARTICLEPRODUCER_STR)
                )
            )

        # add lepton-subtracted generator-level jets to nanoAOD Ntuple
        genjetAK4LSTable_str = 'genJetAK4LSTable'
        if not hasattr(process, genjetAK4LSTable_str):
            setattr(process, genjetAK4LSTable_str,
                process.genJetTable.clone(
                    src = cms.InputTag(genjetAK4LS_str),
                    name = cms.string("GenJetAK4LS"),
                    doc  = cms.string("genJetsAK4LS, i.e. ak4 Jets made with visible genparticles excluding prompt leptons and leptons from tau decays"),
                )
            )

        # add information on generator-level parton flavor to reconstructed jets
        genJetFlavourAssociationAK4LS_str = 'genJetFlavourAssociationAK4LS%s' % suffix
        setattr(process, genJetFlavourAssociationAK4LS_str,
            process.genJetFlavourAssociation.clone(
                jets = cms.InputTag(genjetAK4LS_str)
            )
        )

        genJetFlavourAK4LSTable = 'genJetFlavourAK4LS%sTable' % suffix # NB! must end with 'Table'
        setattr(process, genJetFlavourAK4LSTable,
            process.genJetFlavourTable.clone(
                src = cms.InputTag(genjetAK4LS_str),
                name = cms.string("GenJetAK4LS"),
                jetFlavourInfos = cms.InputTag(genJetFlavourAssociationAK4LS_str)
            )
        )
        #----------------------------------------------------------------------------

    leptonSubtractedJetSequence = cms.Sequence(
        leptonSubtractedPFCandsSequence +
        getattr(process, jetSequenceAK4LS_str) +
        getattr(process, slimmedJetCollectionAK4LS_str) +
        getattr(process, tightJetIdAK4LS_str) +
        getattr(process, tightJetIdLepVetoAK4LS_str) +
        getattr(process, bJetVars_str) +
        getattr(process, qgtagger_str) +
        getattr(process, jetSubStructureVars_str) +
        getattr(process, pileupJetId_str) +
        getattr(process, jetsAK4LSWithUserData_str) +
        getattr(process, bjetNN_str) +
        getattr(process, jetAK4LSTable_str)
    )
    if runOnMC:
        leptonSubtractedJetSequence += getattr(process, genjetAK4LS_str) + getattr(process, genjetAK4LSTable_str)
        leptonSubtractedJetSequence += getattr(process, genJetFlavourAssociationAK4LS_str) + getattr(process, genJetFlavourAK4LSTable)

    #----------------------------------------------------------------------------

    _leptonSubtractedJetSequence_80X = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_80X.replace(getattr(process, tightJetIdLepVetoAK4LS_str), getattr(process, looseJetIdAK4LS_str))
    run2_miniAOD_80XLegacy.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_80X)

    _leptonSubtractedJetSequence_94X2016 = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_94X2016.replace(getattr(process, tightJetIdLepVetoAK4LS_str), getattr(process, looseJetIdAK4LS_str))
    run2_nanoAOD_94X2016.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_94X2016)

    leptonSubtractedJetSequence_str = 'leptonSubtractedJetSequenceAK4LS%s' % suffix
    setattr(process, leptonSubtractedJetSequence_str, leptonSubtractedJetSequence)
    process.nanoSequence += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceMC += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceFS += getattr(process, leptonSubtractedJetSequence_str)
