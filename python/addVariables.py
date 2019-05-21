import FWCore.ParameterSet.Config as cms

from tthAnalysis.NanoAOD.boosted_cff import boostedSequence, boostedTables
from tthAnalysis.NanoAOD.taus_updatedMVAIds_cff import addDeepTau2017v2
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables
from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets

from PhysicsTools.NanoAOD.common_cff import Var, ExtVar
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv1_cff import run2_nanoAOD_94XMiniAODv1
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv2_cff import run2_nanoAOD_94XMiniAODv2
from Configuration.Eras.Modifier_run2_nanoAOD_102Xv1_cff import run2_nanoAOD_102Xv1

from RecoEgamma.EgammaTools.calibratedEgammas_cff import calibratedPatElectrons

from CondCore.CondDB.CondDB_cfi import CondDB

import os.path

def addEScaleSmearing2018(process):
  process.calibratedPatElectrons102X = calibratedPatElectrons.clone(
    produceCalibratedObjs = False,
    correctionFile        = cms.string("tthAnalysis/NanoAOD/data/ScalesSmearings/Run2018_Step2Closure_CoarseEtaR9Gain_v2"),
  )
  run2_nanoAOD_102Xv1.toModify(process.slimmedElectronsWithUserData.userFloats,
    ecalTrkEnergyErrPostCorrNew = cms.InputTag("calibratedPatElectrons102X","ecalTrkEnergyErrPostCorr"),
    ecalTrkEnergyPreCorrNew     = cms.InputTag("calibratedPatElectrons102X","ecalTrkEnergyPreCorr"),
    ecalTrkEnergyPostCorrNew    = cms.InputTag("calibratedPatElectrons102X","ecalTrkEnergyPostCorr"),
  )
  run2_nanoAOD_102Xv1.toModify(process.electronTable.variables,
    pt        = Var(
      "pt*userFloat('ecalTrkEnergyPostCorrNew')/userFloat('ecalTrkEnergyPreCorrNew')",
      float, precision = -1, doc = "p_{T}"
    ),
    energyErr = Var(
      "userFloat('ecalTrkEnergyErrPostCorrNew')",
      float, precision = 6, doc = "energy error of the cluster-track combination"
    ),
    eCorr     = Var(
      "userFloat('ecalTrkEnergyPostCorrNew')/userFloat('ecalTrkEnergyPreCorrNew')",
      float, doc = "ratio of the calibrated energy/miniaod energy"
    ),
  )
  _with102XScale_sequence = process.electronSequence.copy()
  _with102XScale_sequence.replace(
    process.slimmedElectronsWithUserData,
    process.calibratedPatElectrons102X + process.slimmedElectronsWithUserData
  )
  run2_nanoAOD_102Xv1.toReplaceWith(process.electronSequence, _with102XScale_sequence)


def addLepMVA(process):
  baseDir = "tthAnalysis/NanoAOD/data/LepMVA"

  process.electronMVATTH.weightFile = cms.FileInPath(os.path.join(baseDir, "el_BDTG_2017.weights.xml"))
  process.electronMVATTH.variablesOrder = cms.vstring([
    "LepGood_pt",
    "LepGood_eta",
    "LepGood_jetNDauChargedMVASel",
    "LepGood_miniRelIsoCharged",
    "LepGood_miniRelIsoNeutral",
    "LepGood_jetPtRelv2",
    "LepGood_jetDF",
    "LepGood_jetPtRatio",
    "LepGood_dxy",
    "LepGood_sip3d",
    "LepGood_dz",
    "LepGood_mvaFall17V2noIso",
  ])
  process.electronMVATTH.variables.LepGood_jetDF = cms.string(
    "?userCand('jetForLepJetVar').isNonnull()?"
      "max("
          "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+"
          "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+"
          "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'),"
        "0.0"
      ")"
    ":0.0"
  )
  process.electronMVATTH.variables.LepGood_jetPtRatio = cms.string(
    "?userCand('jetForLepJetVar').isNonnull()?min(userFloat('ptRatio'),1.5):1.0/(1.0+userFloat('PFIsoAll04')/pt)"
  )
  process.electronMVATTH.variables.LepGood_mvaFall17V2noIso = cms.string("userFloat('mvaFall17V2noIso')")
  del process.electronMVATTH.variables.LepGood_jetBTagCSV

  process.muonMVATTH.weightFile = cms.FileInPath(os.path.join(baseDir, "mu_BDTG_2017.weights.xml"))
  process.muonMVATTH.variablesOrder = cms.vstring([
    "LepGood_pt",
    "LepGood_eta",
    "LepGood_jetNDauChargedMVASel",
    "LepGood_miniRelIsoCharged",
    "LepGood_miniRelIsoNeutral",
    "LepGood_jetPtRelv2",
    "LepGood_jetDF",
    "LepGood_jetPtRatio",
    "LepGood_dxy",
    "LepGood_sip3d",
    "LepGood_dz",
    "LepGood_segmentComp",
  ])
  process.muonMVATTH.variables.LepGood_jetDF = cms.string(
    "?userCand('jetForLepJetVar').isNonnull()?"
      "max("
        "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+"
        "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+"
        "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'),"
        "0.0"
      ")"
    ":0.0"
  )
  process.muonMVATTH.variables.LepGood_jetPtRatio = cms.string(
    "?userCand('jetForLepJetVar').isNonnull()?"
      "min(userFloat('ptRatio'),1.5):"
      "1.0/"
        "(1.0+"
          "(pfIsolationR04().sumChargedHadronPt + max"
            "("
              "pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,"
              "0.0"
            ")"
          ")/pt"
        ")"
  )
  process.muonMVATTH.variables.LepGood_segmentComp = cms.string("segmentCompatibility")
  del process.muonMVATTH.variables.LepGood_jetBTagCSV
  del process.muonMVATTH.variables.LepGood_segmentCompatibility

  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(
      process.electronMVATTH,
      weightFile = cms.FileInPath(os.path.join(baseDir, "el_BDTG_2016.weights.xml"))
    )
    modifier.toModify(
      process.muonMVATTH,
      weightFile = cms.FileInPath(os.path.join(baseDir, "mu_BDTG_2016.weights.xml"))
    )
    modifier.toModify(
      process.electronMVATTH.variables,
      LepGood_mvaIdSpring16HZZ = None,
    )

  for modifier in run2_nanoAOD_94XMiniAODv1, run2_nanoAOD_94XMiniAODv2, run2_nanoAOD_102Xv1:
    modifier.toModify(
      process.electronMVATTH.variables,
      LepGood_mvaIdFall17noIso = None,
    )

def recomputeQGL(process):
  process.QGPoolDBESSource = cms.ESSource("PoolDBESSource",
    CondDB.clone(
      connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
    ),
    toGet = cms.VPSet(
      cms.PSet(
        record = cms.string('QGLikelihoodRcd'),
        tag    = cms.string('QGLikelihoodObject_v1_AK4PFchs_2017'),
        label  = cms.untracked.string('QGL_AK4PFchs'),
      ),
    ),
  )
  process.es_prefer_qgl = cms.ESPrefer("PoolDBESSource", "QGPoolDBESSource")

def addVariables(process, is_mc, year):
  process.load('tthAnalysis.NanoAOD.boosted_cff')

  process.boostedSequence = boostedSequence
  process.boostedTables = boostedTables
  process.nanoSequence += process.boostedSequence
  process.nanoSequence += process.boostedTables
  process.nanoSequenceMC += process.boostedSequence
  process.nanoSequenceMC += process.boostedTables
  process.nanoSequenceFS += process.boostedSequence
  process.nanoSequenceFS += process.boostedTables

  if not hasattr(process.electronTable.variables, "eCorr"):
    # No electron scale or smearing available for 2018 era, yet:
    # See: https://github.com/cms-sw/cmssw/blob/master/RecoEgamma/EgammaTools/python/calibratedEgammas_cff.py
    print("Branch 'eCorr' not implemented for electrons => filling with placedholder value")
    process.electronTable.variables.eCorr = Var(
      "1.", float, doc = "ratio of the calibrated energy/miniaod energy", precision = 6
    )

  process.electronTable.variables.hoe.precision = cms.int32(12)
  process.electronTable.variables.deltaPhiSC = Var(
    "superCluster().phi()-phi()",
    float, doc = "delta phi (SC,ele) with sign", precision = 10
  )
  process.electronTable.variables.deltaEtaSC_trackatVtx = Var(
    "deltaEtaSuperClusterTrackAtVtx()",
    float, doc = "HLT safe delta eta (SC,ele) with sign", precision = 10
  )
  process.electronTable.variables.deltaPhiSC_trackatVtx = Var(
    "deltaPhiSuperClusterTrackAtVtx()",
    float, doc = "HLT safe delta phi (SC,ele) with sign", precision = 10
  )
  process.electronTable.variables.pfRelIso04_all = Var(
    "userFloat('PFIsoAll04')/pt",
    float, doc = "PF relative isolation dR=0.4, total (with rho*EA PU corrections)"
  )

  process.electronTable.variables.jetNDauChargedMVASel = Var(
    "?userCand('jetForLepJetVar').isNonnull()?userFloat('jetNDauChargedMVASel'):0",
    int, doc = "jetNDauChargedMVASel variable used by TTH MVA"
  )
  process.electronTable.variables.jetPtRelv2 = Var(
    "?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRel'):0",
    float, doc = "jetPtRelv2 variable used by TTH MVA"
  )
  process.electronTable.variables.jetPtRatio = Var(
    "?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRatio'):1.0/(1.0+userFloat('PFIsoAll04')/pt)",
    float, doc = "jetPtRatio variable used by TTH MVA"
  )
  process.electronTable.variables.jetBTagCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags'):"
    "-1.",
    float, doc = "jetBTagCSV variable used by TTH MVA"
  )
  process.electronTable.variables.jetBTagDeepCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probbb'):"
    "-1.",
    float, doc = "jetBTagDeepCSV variable"
  )
  process.electronTable.variables.jetBTagDeepJet = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'):"
    "-1.",
    float, doc = "jetBTagDeepJet variable"
  )

  process.muonTable.variables.jetNDauChargedMVASel = Var(
    "?userCand('jetForLepJetVar').isNonnull()?userFloat('jetNDauChargedMVASel'):0",
    int, doc = "jetNDauChargedMVASel variable used by TTH MVA"
  )
  process.muonTable.variables.jetPtRelv2 = Var(
    "?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRel'):0",
    float, doc = "jetPtRelv2 variable used by TTH MVA"
  )
  process.muonTable.variables.jetPtRatio = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
      "userFloat('ptRatio'):"
      "1.0/("
        "1.0+("
          "pfIsolationR04().sumChargedHadronPt + max("
            "pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,"
            "0.0"
          ")"
        ")/pt"
      ")",
    float, doc = "jetPtRatio variable used by TTH MVA"
  )
  process.muonTable.variables.jetBTagCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags'):"
    "-1.",
    float, doc = "jetBTagCSV variable used by TTH MVA"
  )
  process.muonTable.variables.jetBTagDeepCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probbb'):"
    "-1.",
    float, doc = "jetBTagDeepCSV variable"
  )
  process.muonTable.variables.jetBTagDeepJet = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:probbb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepFlavourJetTags:problepb'):"
    "-1.",
    float, doc = "jetBTagDeepJet variable"
  )

  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(
      process.electronTable.variables,
      jetRelIso = Var(
        "?userCand('jetForLepJetVar').isNonnull()?(1./userFloat('ptRatio'))-1.:userFloat('PFIsoAll04')/pt",
        float, doc = "Relative isolation in matched jet"
      )
    )
    modifier.toModify(
      process.muonTable.variables,
      jetRelIso = Var(
        "?userCand('jetForLepJetVar').isNonnull()?"
        "(1./userFloat('ptRatio'))-1.:"
        "(pfIsolationR04().sumChargedHadronPt + "
          "max(pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0)"
        ")/pt",
        float, doc = "Relative isolation in matched jet"
      )
    )

  process.jetTable.variables.btagDeepCvsL = Var(
    "bDiscriminator('pfDeepCSVJetTags:probc')/"
    "(bDiscriminator('pfDeepCSVJetTags:probc') + bDiscriminator('pfDeepCSVJetTags:probudsg'))",
    float, doc = "DeepCSV Charm vs Light Jet (udsg) b-tag discriminator", precision = 10
  )
  process.jetTable.variables.btagDeepCvsB = Var(
    "bDiscriminator('pfDeepCSVJetTags:probc')/("
      "bDiscriminator('pfDeepCSVJetTags:probc') + bDiscriminator('pfDeepCSVJetTags:probb') + "
      "bDiscriminator('pfDeepCSVJetTags:probbb')"
    ")",
    float, doc = "DeepCSV Charm vs b,b+bb b-tag discriminator", precision = 10
  )
  process.jetTable.variables.puIdDisc = Var(
    "userFloat('pileupJetId:fullDiscriminant')",
    float, doc = "Pilup ID discriminant", precision = 10
  )

  process.metTable.variables.covXX = Var(
    "getSignificanceMatrix().At(0,0)",
    float, doc = "xx element of met covariance matrix", precision = 8
  )
  process.metTable.variables.covXY = Var(
    "getSignificanceMatrix().At(0,1)",
    float, doc = "xy element of met covariance matrix", precision = 8
  )
  process.metTable.variables.covYY = Var(
    "getSignificanceMatrix().At(1,1)",
    float, doc = "yy element of met covariance matrix", precision = 8
  )
  process.metTable.variables.significance = Var(
    "metSignificance()",
    float, doc = "MET significance", precision = 10
  )

  for modifier in run2_nanoAOD_94XMiniAODv1, run2_nanoAOD_94XMiniAODv2:
    modifier.toModify(
      process.metTable,
      src = cms.InputTag("slimmedMETsFixEE2017"),
      doc = cms.string("Type-1 corrected PF MET, with fixEE2017 definition"),
    )
    modifier.toModify(
      process.metFixEE2017Table,
      src  = cms.InputTag("slimmedMETs"),
      name = cms.string("METUnFixedEE2017"),
      doc  = cms.string("slimmedMET, type-1 corrected PF MET"),
    )

  addJetSubstructureObservables(process) # adds nothing to VSIZE
  # enabling one addLeptonSubtractedAK8Jets() adds 10MB to VSIZE but enabling the second one doesn't increase the VSIZE
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = True)
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = False)
  addDeepTau2017v2(process)
  recomputeQGL(process)
  addLepMVA(process)
  addEScaleSmearing2018(process)
