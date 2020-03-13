import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

def addLeptonSubtractedPFCands(process, era, useFakeable):

    assert(era in [ "2016", "2017", "2018" ])
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

    # run PUPPI algorithm (arXiv:1407.6013) on cleaned packedPFCandidates collection
    # cf. https://twiki.cern.ch/twiki/bin/view/CMS/JetToolbox#New_PF_Collection
    from CommonTools.PileupAlgos.Puppi_cff import puppi
    leptonLesspuppi_str = 'leptonLesspuppi%s' % suffix
    if not hasattr(process, leptonLesspuppi_str):
        setattr(process, leptonLesspuppi_str,
            puppi.clone(
                candName = cms.InputTag(leptonLessPFProducer_str),
                vertexName = cms.InputTag("offlineSlimmedPrimaryVertices"),
                useExistingWeights = cms.bool(True)
            )
        )
    #----------------------------------------------------------------------------

    leptonSubtractedPFCandsSequence_str = 'leptonSubtractedPFCandsSequence%s' % suffix    
    if not hasattr(process, leptonSubtractedPFCandsSequence_str):
        setattr(process, leptonSubtractedPFCandsSequence_str, 
            cms.Sequence(
                getattr(process, electronCollectionTTH_str) + getattr(process, muonCollectionTTH_str) + \
                getattr(process, leptonLessPFProducer_str) + getattr(process, leptonLesspuppi_str) 
            )
        )
    return ( getattr(process, leptonSubtractedPFCandsSequence_str), leptonLesspuppi_str )
