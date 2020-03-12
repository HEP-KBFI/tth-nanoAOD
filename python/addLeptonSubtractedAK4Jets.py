import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016
from tthAnalysis.NanoAOD.addLeptonSubtractedPFCands import addLeptonSubtractedPFCands

def addLeptonSubtractedAK4Jets(process, runOnMC, era, useFakeable):

    assert(era in [ "2016", "2017", "2018" ])
    suffix = "Fakeable" if useFakeable else "Loose"

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to loose or fakeable electrons or muons
    leptonSubtractedPFCandsSequence = addLeptonSubtractedPFCands(process, era, useFakeable)
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # reconstruct lepton-subtracted AK4 jets
    from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox
    bTagDiscriminators = [
        'pfCombinedInclusiveSecondaryVertexV2BJetTags', 
        'pfCombinedMVAV2BJetTags', 'pfDeepCSVJetTags:probb', 'pfDeepCSVJetTags:probbb', 'pfDeepCSVJetTags:probc',
        'pfDeepFlavourJetTags:probb', 'pfDeepFlavourJetTags:probbb', 'pfDeepFlavourJetTags:problepb'
    ]
    JETCorrLevels = [ 'L1FastJet', 'L2Relative', 'L3Absolute' ]
    if not runOnMC:
        JETCorrLevels.append('L2L3Residual')

    jetSequenceAK4LS_str = 'jetSequenceAK4LS%s' % suffix
    NoLep_str = 'NoLep%s' % suffix
    jetToolbox(
        proc = process, jetType = 'ak4', jetSequence = jetSequenceAK4LS_str, outputFile = 'out', PUMethod = 'Puppi',
        JETCorrPayload = 'AK4PFPuppi', postFix = NoLep_str, JETCorrLevels = JETCorrLevels, miniAOD = True,
        runOnMC = runOnMC, newPFCollection = True, nameNewPFCollection = leptonLesspuppi_str, 
        bTagDiscriminators = bTagDiscriminators
    )
    jetCollectionAK4LS_str = 'packedPatJetsAK4PFPuppi%s' % NoLep_str
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

    from RecoJets.JetProducers.QGTagger_cfi import QGTagger
    qgtagger_str = 'qgtaggerAK4LS%s' % suffix
    setattr(process, qgtagger_str,
        process.qgtagger.clone(
            srcJets = cms.InputTag(jetCollectionAK4LS_str)
        )
    )

    jetsAK4LSWithUserData_str = 'jetsAK8LSWithUserData%s' % suffix
    setattr(process, jetsAK4LSWithUserData_str,
        process.updatedJetsWithUserData.clone(
            src = cms.InputTag(jetCollectionAK8LS_str),
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
            ),
            userInts = cms.PSet(
                tightId = cms.InputTag(tightJetIdAK4LS_str),
                tightIdLepVeto = cms.InputTag(tightJetIdLepVetoAK4LS_str),
                vtxNtrk = cms.InputTag("%s:vtxNtrk" % bJetVars_str),
                leptonPdgId = cms.InputTag("%s:leptonPdgId" % bJetVars_str),
            )
        )
    )
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(getattr(process, jetsAK4LSWithUserData_str).userInts,
            looseId = cms.InputTag("looseJetId"),
        )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add lepton-subtracted AK4 jets to nanoAOD Ntuple
    jetAK4LSTable_str = 'jetAK4LS%sTable' % suffix # NB! must end with 'Table'
    setattr(process, jetAK4LSTable_str,
        process.jetTable.clone(
            src = cms.InputTag(jetsAK4LSWithUserData_str),
            name = cms.string("JetAK4LS%s" % suffix),
            doc = cms.string("lepton-subtracted ak4 jets"),
            externalVariables = cms.PSet(
                #bRegOld = ExtVar(cms.InputTag("bjetMVA"),float, doc="pt corrected with b-jet regression",precision=14),
                bRegCorr = ExtVar(cms.InputTag("bjetNN:corr"),float, doc="pt correction for b-jet energy regression",precision=12),
                bRegRes = ExtVar(cms.InputTag("bjetNN:res"),float, doc="res on pt corrected with b-jet regression",precision=8),
            )
        )
    )

    ### Era dependent customization
    for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
        modifier.toModify(getattr(process, jetAK4LSTable_str).variables, 
          jetId = Var("userInt('tightIdLepVeto')*4+userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight, bit3 is tightLepVeto"))

    leptonSubtractedJetSequence = cms.Sequence(
        leptonSubtractedPFCandsSequence + \
        getattr(process, jetSequenceAK8LS_str) + getattr(process, tightJetIdAK8LS_str) + \
        getattr(process, tightJetIdLepVetoAK8LS_str) + getattr(process, subStructureAK8_str) + \
        getattr(process, bJetVars_str) + getattr(process, qgtagger_str) + getattr(process, jetsAK8LSWithUserData_str) + getattr(process, subStructureSubJetAK8_str) + \
        getattr(process, subJetsAK8LSWithUserData_str) + getattr(process, fatJetAK8LSTable_str) + \
        getattr(process, subJetAK8LSTable_str)
    )
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
