import FWCore.ParameterSet.Config as cms

from RecoJets.Configuration.GenJetParticles_cff import genParticlesForJetsNoNu

from CommonTools.PileupAlgos.Puppi_cff import puppi

GENPARTICLESFORJETSNONU_STR = 'genParticlesForJetsNoNu'
LEPTONLESSGENPARTICLEPRODUCER_STR = 'leptonLessGenParticles'

def addLeptonSubtractedPFCands(process, era, useFakeable, puMethod, runOnMC):

    assert(era in [ "2016", "2017", "2018" ])
    assert(puMethod in [ 'chs', 'puppi' ])
    suffix = "Fakeable" if useFakeable else "Loose"

    #----------------------------------------------------------------------------
    # produce collections of electrons and muons passing loose or fakeable lepton selection of ttH multilepton+tau analysis (HIG-18-019)
    electronCollectionTTH_str = 'electronCollectionTTH%s' % suffix
    if not hasattr(process, electronCollectionTTH_str):
        setattr(process, electronCollectionTTH_str,
            cms.EDProducer("PATElectronSelector%s" % suffix,
                src = cms.InputTag("linkedObjects", "electrons"),
                src_mvaTTH = cms.InputTag("electronMVATTH"),
                era = cms.string(era),
                debug = cms.bool(False)
            )
        )
    muonCollectionTTH_str = 'muonCollectionTTH%s' % suffix
    if not hasattr(process, muonCollectionTTH_str):
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
    if not hasattr(process, leptonLessPFProducer_str):
        setattr(process, leptonLessPFProducer_str,
            cms.EDProducer('LeptonLessPFProducer',
                src_pfCands = cms.InputTag("packedPFCandidates"),
                src_electrons = cms.InputTag(electronCollectionTTH_str),
                src_muons = cms.InputTag(muonCollectionTTH_str),
                debug = cms.bool(False)
            )
        )

    leptonLessPU_str = 'leptonLess%s%s' % (puMethod, suffix)
    if puMethod == 'puppi':
        # run PUPPI algorithm (arXiv:1407.6013) on cleaned packedPFCandidates collection
        # cf. https://twiki.cern.ch/twiki/bin/view/CMS/JetToolbox#New_PF_Collection
        if not hasattr(process, leptonLessPU_str):
            setattr(process, leptonLessPU_str,
                puppi.clone(
                    candName = cms.InputTag(leptonLessPFProducer_str),
                    vertexName = cms.InputTag("offlineSlimmedPrimaryVertices"),
                    useExistingWeights = cms.bool(True)
                )
            )
    elif puMethod == 'chs':
        leptonLessCands_tmp1 = '%stmp1' % leptonLessPU_str
        leptonLessCands_tmp2 = '%stmp2' % leptonLessPU_str
        setattr(process, leptonLessCands_tmp1,
            cms.EDFilter("CandPtrSelector",
                src = cms.InputTag("packedPFCandidates"),
                cut = cms.string("fromPV"),
            )
        )
        setattr(process, leptonLessCands_tmp2,
            cms.EDProducer("CandPtrProjector",
                src = cms.InputTag(leptonLessCands_tmp1),
                veto = cms.InputTag(muonCollectionTTH_str),
            )
        )
        setattr(process, leptonLessPU_str,
            cms.EDProducer("CandPtrProjector",
                src = cms.InputTag(leptonLessCands_tmp2),
                veto = cms.InputTag(electronCollectionTTH_str),
            )
        )
    else:
        raise RuntimeError("Invalid PU method: %s" % puMethod)
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # produce collection of generator-level particles excluding prompt leptons and leptons from tau decays
    # (used to produce lepton-subtracted generator-level jets)
    # NB.: Selection taken from the Higgs->tautau twiki
    #        https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauWorking2016#MC_Matching
    if runOnMC:
        if not hasattr(process, GENPARTICLESFORJETSNONU_STR):
            setattr(process, GENPARTICLESFORJETSNONU_STR,
                    genParticlesForJetsNoNu.clone(
                    src = cms.InputTag("prunedGenParticles"),
                )
            )
        if not hasattr(process, LEPTONLESSGENPARTICLEPRODUCER_STR):
            setattr(process, LEPTONLESSGENPARTICLEPRODUCER_STR,
                    cms.EDFilter("CandPtrSelector",
                             src = cms.InputTag(GENPARTICLESFORJETSNONU_STR),
                             cut = cms.string('!(pt > 8 & (abs(pdgId) = 11 | abs(pdgId) = 13) & (isPromptFinalState | isDirectPromptTauDecayProductFinalState))'),
                             stableOnly = cms.bool(True),
                             filter = cms.bool(False),
                         )
                    )
    #----------------------------------------------------------------------------

    leptonSubtractedPFCandsSequence_str = 'leptonSubtractedPFCandsSequence%s%s' % (puMethod, suffix)
    if not hasattr(process, leptonSubtractedPFCandsSequence_str):
        if puMethod == 'puppi':
            setattr(process, leptonSubtractedPFCandsSequence_str,
                cms.Sequence(
                    getattr(process, electronCollectionTTH_str) + getattr(process, muonCollectionTTH_str) + \
                    getattr(process, leptonLessPFProducer_str) + getattr(process, leptonLessPU_str)
                )
            )
        elif puMethod == 'chs':
            setattr(process, leptonSubtractedPFCandsSequence_str,
                cms.Sequence(
                    getattr(process, electronCollectionTTH_str) + getattr(process, muonCollectionTTH_str) + \
                    getattr(process, leptonLessPFProducer_str) + getattr(process, leptonLessCands_tmp1) + \
                    getattr(process, leptonLessCands_tmp2) + getattr(process, leptonLessPU_str)
                )
            )
        else:
            raise RuntimeError("Invalid PU method: %s" % puMethod)
        if runOnMC:
            leptonSubtractedPFCandsSequence = getattr(process, leptonSubtractedPFCandsSequence_str)
            leptonSubtractedPFCandsSequence += getattr(process, GENPARTICLESFORJETSNONU_STR) + \
                                               getattr(process, LEPTONLESSGENPARTICLEPRODUCER_STR)
    return ( getattr(process, leptonSubtractedPFCandsSequence_str), leptonLessPU_str )
