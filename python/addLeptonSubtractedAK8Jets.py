import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

from RecoJets.JetProducers.ECF_cff import ecfNbeta1
from RecoJets.JetProducers.nJettinessAdder_cfi import Njettiness
from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder

from tthAnalysis.NanoAOD.addLeptonSubtractedPFCands import addLeptonSubtractedPFCands
from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox

def addLeptonSubtractedAK8Jets(process, runOnMC, era, useFakeable, addQJets = False):

    assert(era in [ "2016", "2017", "2018" ])
    suffix = "Fakeable" if useFakeable else "Loose"

    #----------------------------------------------------------------------------
    # produce collection of packedPFCandidates not associated to loose or fakeable electrons or muons
    ( leptonSubtractedPFCandsSequence, leptonLessPU_str ) = addLeptonSubtractedPFCands(process, era, useFakeable, 'puppi')
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # reconstruct lepton-subtracted AK8 jets
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
        runOnMC = runOnMC, newPFCollection = True, nameNewPFCollection = leptonLessPU_str, addSoftDrop = True,
        addSoftDropSubjets = True, addNsub = True, subJETCorrPayload = 'AK4PFPuppi', subJETCorrLevels = JETCorrLevels,
        bTagDiscriminators = bTagDiscriminators
    )
    # CV: fix ordering of modules in jet sequence
    #    (NjettinessAK8PuppiNoLep needs to be run before selectedPatJetsAK8PFPuppiNoLepSoftDropPacked)
    jetSequenceAK8LS = getattr(process, jetSequenceAK8LS_str)
    NjettinessAK8Puppi_str = 'NjettinessAK8Puppi%s' % NoLep_str
    jetSequenceAK8LS.remove(getattr(process, NjettinessAK8Puppi_str))
    jetSequenceAK8LS.replace(
        getattr(process, 'selectedPatJetsAK8PFPuppi%sSoftDropPacked' % NoLep_str),
        getattr(process, NjettinessAK8Puppi_str) + \
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
    # add PF jet ID flags and jet energy corrections for AK4 pat::Jet collection,
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
    nb1AK8PuppiSoftDrop_str = 'nb1AK8PuppiSoftDrop%s' % suffix
    setattr(process, nb1AK8PuppiSoftDrop_str,
            ecfNbeta1.clone(
                src = cms.InputTag(fatJetCollectionAK8LS_str),
                cuts = cms.vstring('', '', 'pt > 250'),
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
                n2b1 = cms.InputTag("%s:ecfN2" % nb1AK8PuppiSoftDrop_str),
                n3b1 = cms.InputTag("%s:ecfN3" % nb1AK8PuppiSoftDrop_str),
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
    ecfNbeta1_str = "nb1AK8LSPuppiSoftDropSubjets%s" % suffix
    setattr(process, ecfNbeta1_str,
        ecfNbeta1.clone(
            src = cms.InputTag(subJetCollectionAK8LS_str),
        )
    )
    Njettiness_str = "NjettinessAK8LSSubjets%s" % suffix
    setattr(process, Njettiness_str,
        Njettiness.clone(
            src = cms.InputTag(subJetCollectionAK8LS_str),
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
                n2b1 = cms.InputTag("%s:ecfN2" % ecfNbeta1_str),
                n3b1 = cms.InputTag("%s:ecfN3" % ecfNbeta1_str),
                tau1 = cms.InputTag("%s:tau1" % Njettiness_str),
                tau2 = cms.InputTag("%s:tau2" % Njettiness_str),
                tau3 = cms.InputTag("%s:tau3" % Njettiness_str),
                tau4 = cms.InputTag("%s:tau4" % Njettiness_str),
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
        )
    )
    fatJetAK8LSTable = getattr(process, fatJetAK8LSTable_str)
    fatJetAK8LSTable.variables.msoftdrop.expr = cms.string("userFloat('ak8PFJetsPuppi%sSoftDropMass')" % NoLep_str)
    fatJetAK8LSTable.variables.subJetIdx1.expr = cms.string("?subjets('SoftDrop').size()>0?subjets('SoftDrop').at(0).key():-1")
    fatJetAK8LSTable.variables.subJetIdx2.expr = cms.string("?subjets('SoftDrop').size()>1?subjets('SoftDrop').at(1).key():-1")
    fatJetAK8LSTable.variables.tau1.expr = cms.string("userFloat('%s:tau1')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.tau2.expr = cms.string("userFloat('%s:tau2')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.tau3.expr = cms.string("userFloat('%s:tau3')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.tau4.expr = cms.string("userFloat('%s:tau4')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.tau4.expr = cms.string("userFloat('%s:tau4')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.tau4.expr = cms.string("userFloat('%s:tau4')" % NjettinessAK8Puppi_str)
    fatJetAK8LSTable.variables.n2b1.expr = cms.string("userFloat('n2b1')")
    fatJetAK8LSTable.variables.n3b1.expr = cms.string("userFloat('n3b1')")
    if addQJets:
        fatJetAK8LSTable.variables.QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10)
        print("Adding Qjet volatility to %s" % jetsAK8LSWithUserData_str)
    else:
        print("NOT adding Qjet volatility to %s" % jetsAK8LSWithUserData_str)

    #----------------------------------------------------------------------------

    if runOnMC:
        #----------------------------------------------------------------------------
        # produce lepton-subtracted generator-level jets
        from RecoJets.JetProducers.ak8GenJets_cfi import ak8GenJets
        genjetAK8LS_str = 'genJetAK8LS'
        setattr(process, genjetAK8LS_str,
            ak8GenJets.clone(
                src = cms.InputTag("leptonLessGenParticles")
            )
        )

        # add lepton-subtracted generator-level jets to nanoAOD Ntuple
        genjetAK8LSTable_str = 'genJetAK8LSTable'
        setattr(process, genjetAK8LSTable_str,
            process.genJetAK8Table.clone(
                src = cms.InputTag(genjetAK8LS_str),
                name = cms.string("GenJetAK8LS"),
                doc  = cms.string("genJetsAK8LS, i.e. ak8 Jets made with visible genparticles excluding prompt leptons and leptons from tau decays"),
            )
        )

        # add information on generator-level parton flavor to reconstructed jets
        genJetFlavourAssociationAK8LS_str = 'genJetFlavourAssociationAK8LS%s' % suffix
        setattr(process, genJetFlavourAssociationAK8LS_str,
            process.genJetAK8FlavourAssociation.clone(
                jets = cms.InputTag(genjetAK8LS_str)
            )
        )

        genJetFlavourAK8LSTable = 'genJetFlavourAK8LS%sTable' % suffix # NB! must end with 'Table'
        setattr(process, genJetFlavourAK8LSTable,
            process.genJetAK8FlavourTable.clone(
                src = cms.InputTag(genjetAK8LS_str),
                name = cms.string("GenJetAK8LS"),
                jetFlavourInfos = cms.InputTag(genJetFlavourAssociationAK8LS_str)
            )
        )
    #----------------------------------------------------------------------------
    subJetAK8LSTable_str = 'subJetAK8LS%sTable' % suffix # NB! must end with 'Table'
    setattr(process, subJetAK8LSTable_str,
        process.subJetTable.clone(
            src = cms.InputTag(subJetsAK8LSWithUserData_str),
            cut = cms.string(""),
            name = cms.string("SubJetAK8LS%s" % suffix),
            doc = cms.string("lepton-subtracted ak8  sub-jets for boosted analysis"),
        )
    )
    subJetAK8LSTable = getattr(process, subJetAK8LSTable_str)
    for var in [ 'n2b1', 'n3b1', 'tau1', 'tau2', 'tau3', 'tau4' ]:
        getattr(subJetAK8LSTable.variables, var).expr = cms.string("userFloat('%s')" % var)
    run2_miniAOD_80XLegacy.toModify(subJetAK8LSTable.variables, btagCMVA = None, btagDeepB = None)

    leptonSubtractedJetSequence = cms.Sequence(
        leptonSubtractedPFCandsSequence +
        getattr(process, jetSequenceAK8LS_str) +
        getattr(process, tightJetIdAK8LS_str) +
        getattr(process, tightJetIdLepVetoAK8LS_str) +
        getattr(process, subStructureAK8_str) +
        getattr(process, nb1AK8PuppiSoftDrop_str) +
        getattr(process, jetsAK8LSWithUserData_str) +
        getattr(process, subStructureSubJetAK8_str) +
        getattr(process, ecfNbeta1_str) +
        getattr(process, Njettiness_str) +
        getattr(process, subJetsAK8LSWithUserData_str) +
        getattr(process, fatJetAK8LSTable_str) +
        getattr(process, subJetAK8LSTable_str)
    )
    if addQJets:
        leptonSubtractedJetSequence.replace(
            getattr(process, jetsAK8LSWithUserData_str),
            getattr(process, QJetsAdderAK8LS_str) +
            getattr(process, jetsAK8LSWithUserData_str)
        )
    if runOnMC:
        leptonSubtractedJetSequence += getattr(process, genjetAK8LS_str) + getattr(process, genjetAK8LSTable_str)
        leptonSubtractedJetSequence += getattr(process, genJetFlavourAssociationAK8LS_str) + getattr(process, genJetFlavourAK8LSTable)

    #----------------------------------------------------------------------------

    _leptonSubtractedJetSequence_80X = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_80X.replace(getattr(process, tightJetIdLepVetoAK8LS_str), getattr(process, looseJetIdAK8LS_str))
    run2_miniAOD_80XLegacy.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_80X)

    _leptonSubtractedJetSequence_94X2016 = leptonSubtractedJetSequence.copy()
    _leptonSubtractedJetSequence_94X2016.replace(getattr(process, tightJetIdLepVetoAK8LS_str), getattr(process, looseJetIdAK8LS_str))
    run2_nanoAOD_94X2016.toReplaceWith(leptonSubtractedJetSequence, _leptonSubtractedJetSequence_94X2016)

    leptonSubtractedJetSequence_str = 'leptonSubtractedJetSequenceAK8LS%s' % suffix
    setattr(process, leptonSubtractedJetSequence_str, leptonSubtractedJetSequence)
    process.nanoSequence += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceMC += getattr(process, leptonSubtractedJetSequence_str)
    process.nanoSequenceFS += getattr(process, leptonSubtractedJetSequence_str)
