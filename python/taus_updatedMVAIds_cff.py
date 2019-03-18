import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var
from PhysicsTools.NanoAOD.taus_cff import _tauId5WPMask, _variables80X, _variablesMiniV1, _variablesMiniV2

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv1_cff import run2_nanoAOD_94XMiniAODv1
from Configuration.Eras.Modifier_run2_nanoAOD_92X_cff import run2_nanoAOD_92X

## Raw
from RecoTauTag.RecoTau.PATTauDiscriminationAgainstElectronMVA6_cfi import patTauDiscriminationAgainstElectronMVA6
from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants

## anti-e 2018 WPs
from RecoTauTag.RecoTau.PATTauDiscriminantCutMultiplexer_cfi import patTauDiscriminantCutMultiplexer

#TODO implement
# deepTau2017v1
# DPFTau_2016_v0
# DPFTau_2016_v1
# from https://github.com/cms-sw/cmssw/blob/master/RecoTauTag/RecoTau/python/tools/runTauIdMVA.py
# see more from
# https://github.com/cms-sw/cmssw/blob/master/RecoTauTag/RecoTau/test/runDeepTauIDsOnMiniAOD.py
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Running_of_the_DNN_based_tau_ID
# https://twiki.cern.ch/twiki/bin/view/CMS/TauIDRecommendation13TeV

def addTauAntiEleMVA2018(process):

  ### Define new anit-e discriminants
  antiElectronDiscrMVA6_version = "MVA6v3_noeveto"

  process.patTauDiscriminationByElectronRejectionMVA62018Raw = patTauDiscriminationAgainstElectronMVA6.clone(
      Prediscriminants = noPrediscriminants, #already selected for MiniAOD
      vetoEcalCracks = False, #keep tau candidates in EB-EE cracks
      mvaName_NoEleMatch_wGwoGSF_BL = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL',
      mvaName_NoEleMatch_wGwoGSF_EC = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC',
      mvaName_NoEleMatch_woGwoGSF_BL = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL',
      mvaName_NoEleMatch_woGwoGSF_EC = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC',
      mvaName_wGwGSF_BL = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL',
      mvaName_wGwGSF_EC = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC',
      mvaName_woGwGSF_BL = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL',
      mvaName_woGwGSF_EC = 'RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC'
  )

  # VLoose
  process.patTauDiscriminationByVLooseElectronRejectionMVA62018 = patTauDiscriminantCutMultiplexer.clone(
      PATTauProducer = process.patTauDiscriminationByElectronRejectionMVA62018Raw.PATTauProducer,
      Prediscriminants = process.patTauDiscriminationByElectronRejectionMVA62018Raw.Prediscriminants,
      toMultiplex = cms.InputTag("patTauDiscriminationByElectronRejectionMVA62018Raw"),
      key = cms.InputTag("patTauDiscriminationByElectronRejectionMVA62018Raw","category"),
      mapping = cms.VPSet(
          cms.PSet(
              category = cms.uint32(0),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(2),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(5),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(7),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(8),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(10),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(13),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC_WPeff98'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(15),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC_WPeff98'),
              variable = cms.string('pt')
          )
      )
  )
  # Loose
  process.patTauDiscriminationByLooseElectronRejectionMVA62018 = process.patTauDiscriminationByVLooseElectronRejectionMVA62018.clone(
      mapping = cms.VPSet(
          cms.PSet(
              category = cms.uint32(0),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(2),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(5),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(7),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(8),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(10),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(13),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC_WPeff90'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(15),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC_WPeff90'),
              variable = cms.string('pt')
          )
      )
  )
  # Medium
  process.patTauDiscriminationByMediumElectronRejectionMVA62018 = process.patTauDiscriminationByVLooseElectronRejectionMVA62018.clone(
      mapping = cms.VPSet(
          cms.PSet(
              category = cms.uint32(0),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(2),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(5),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(7),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(8),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(10),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(13),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC_WPeff80'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(15),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC_WPeff80'),
              variable = cms.string('pt')
          )
      )
  )
  # Tight
  process.patTauDiscriminationByTightElectronRejectionMVA62018 = process.patTauDiscriminationByVLooseElectronRejectionMVA62018.clone(
      mapping = cms.VPSet(
          cms.PSet(
              category = cms.uint32(0),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(2),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(5),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(7),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(8),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(10),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(13),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC_WPeff70'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(15),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC_WPeff70'),
              variable = cms.string('pt')
          )
      )
  )
  # VTight
  process.patTauDiscriminationByVTightElectronRejectionMVA62018 = process.patTauDiscriminationByVLooseElectronRejectionMVA62018.clone(
      mapping = cms.VPSet(
          cms.PSet(
              category = cms.uint32(0),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_BL_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(2),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_BL_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(5),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_BL_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(7),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_BL_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(8),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_woGwoGSF_EC_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(10),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_NoEleMatch_wGwoGSF_EC_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(13),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_woGwGSF_EC_WPeff60'),
              variable = cms.string('pt')
          ),
          cms.PSet(
              category = cms.uint32(15),
              cut = cms.string('RecoTauTag_antiElectron'+antiElectronDiscrMVA6_version+'_gbr_wGwGSF_EC_WPeff60'),
              variable = cms.string('pt')
          )
      )
  )
  ### Put all anti-e tau-IDs into a sequence
  process.patTauDiscriminationByElectronRejectionSeq = cms.Sequence(
      process.patTauDiscriminationByElectronRejectionMVA62018Raw
      +process.patTauDiscriminationByVLooseElectronRejectionMVA62018
      +process.patTauDiscriminationByLooseElectronRejectionMVA62018
      +process.patTauDiscriminationByMediumElectronRejectionMVA62018
      +process.patTauDiscriminationByTightElectronRejectionMVA62018
      +process.patTauDiscriminationByVTightElectronRejectionMVA62018
  )

  _antiETauIDSources = cms.PSet(
      againstElectronMVA6Raw2018 = cms.InputTag("patTauDiscriminationByElectronRejectionMVA62018Raw"),
      againstElectronMVA6category2018 = cms.InputTag("patTauDiscriminationByElectronRejectionMVA62018Raw","category"),
      againstElectronVLooseMVA62018 = cms.InputTag("patTauDiscriminationByVLooseElectronRejectionMVA62018"),
      againstElectronLooseMVA62018 = cms.InputTag("patTauDiscriminationByLooseElectronRejectionMVA62018"),
      againstElectronMediumMVA62018 = cms.InputTag("patTauDiscriminationByMediumElectronRejectionMVA62018"),
      againstElectronTightMVA62018 = cms.InputTag("patTauDiscriminationByTightElectronRejectionMVA62018"),
      againstElectronVTightMVA62018 = cms.InputTag("patTauDiscriminationByVTightElectronRejectionMVA62018")
  )

  process.patTauMVAIDsSeq.insert(
    process.patTauMVAIDsSeq.index(process.slimmedTausUpdated),
    process.patTauDiscriminationByElectronRejectionSeq
  )
  _tauIDSourcesWithAntiE = cms.PSet(
    process.slimmedTausUpdated.tauIDSources.clone(),
    _antiETauIDSources
  )
  process.slimmedTausUpdated.tauIDSources = _tauIDSourcesWithAntiE

  _variablesMiniV2.rawAntiEle2018    = Var(
    "tauID('againstElectronMVA6Raw2018')",
    float, doc = "Anti-electron MVA discriminator V6 raw output discriminator (2018)", precision = 10
  )
  _variablesMiniV2.rawAntiEleCat2018 = Var(
    "tauID('againstElectronMVA6category2018')",
    int, doc = "Anti-electron MVA discriminator V6 category (2018)"
  )
  _variablesMiniV2.idAntiEle2018     = _tauId5WPMask(
    "againstElectron%sMVA62018", doc = "Anti-electron MVA discriminator V6 (2018)"
  )
  process.tauTable.variables = _variablesMiniV2

  for modifier in run2_nanoAOD_94XMiniAODv1, run2_nanoAOD_92X:
    modifier.toModify(process.tauTable, variables = _variablesMiniV1)
  run2_miniAOD_80XLegacy.toModify(process.tauTable, variables = _variables80X)
