import FWCore.ParameterSet.Config as cms

from tthAnalysis.NanoAOD.boosted_cff import boostedSequence, boostedTables
from tthAnalysis.NanoAOD.taus_updatedMVAIds_cff import addTauAntiEleMVA2018
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables
from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets

from PhysicsTools.NanoAOD.common_cff import Var
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016

def addVariables(process, is_mc, year, is_th = False):
  assert(is_mc or not is_th)
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
    "max(userCand('jetForLepJetVar').bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags'),0.0):"
    "0.0",
    float, doc = "jetBTagCSV variable used by TTH MVA"
  )
  process.electronTable.variables.jetBTagDeepCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probbb'):"
    "-1.",
    float, doc = "jetBTagDeepCSV variable"
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
    "1.0/(1.0+(pfIsolationR04().sumChargedHadronPt + max("
      "pfIsolationR04().sumNeutralHadronEt + pfIsolationR04().sumPhotonEt - pfIsolationR04().sumPUPt/2,0.0"
    "))/pt)",
    float, doc = "jetPtRatio variable used by TTH MVA"
  )
  process.muonTable.variables.jetBTagCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "max(userCand('jetForLepJetVar').bDiscriminator('pfCombinedInclusiveSecondaryVertexV2BJetTags'),0.0):"
    "0.0",
    float, doc = "jetBTagCSV variable used by TTH MVA"
  )
  process.muonTable.variables.jetBTagDeepCSV = Var(
    "?userCand('jetForLepJetVar').isNonnull()?"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probb')+"
    "userCand('jetForLepJetVar').bDiscriminator('pfDeepCSVJetTags:probbb'):"
    "-1.",
    float, doc = "jetBTagDeepCSV variable"
  )

  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(
      process.electronTable.variables,
      jetPtRatio = Var(
        "?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRatio'):1",
        float, doc = "jetPtRatio variable used by TTH MVA"
      )
    )
    modifier.toModify(
      process.muonTable.variables,
      jetPtRatio = Var(
        "?userCand('jetForLepJetVar').isNonnull()?userFloat('ptRatio'):1",
        float, doc = "jetPtRatio variable used by TTH MVA"
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

  if is_th:
    print("Enabling tH weights")
    process.genWeightsTable.namedWeightIDs = cms.vstring(*tuple(map(lambda x: 'rwgt_%d' % x, range(1, 70))))
    process.genWeightsTable.namedWeightLabels = cms.vstring(*tuple(map(lambda x: 'rwgt_%d' % x, range(1, 70))))

  addJetSubstructureObservables(process)
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = True)
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = False)
  addTauAntiEleMVA2018(process)
