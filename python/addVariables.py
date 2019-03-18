import FWCore.ParameterSet.Config as cms

from tthAnalysis.NanoAOD.boosted_cff import boostedSequence, boostedTables
from tthAnalysis.NanoAOD.taus_updatedMVAIds_cff import addTauAntiEleMVA2018, addDeepTau2017v1, addDPFTau_2016_v0, addDPFTau_2016_v1
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables
from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets

from PhysicsTools.NanoAOD.common_cff import Var, ExtVar
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv1_cff import run2_nanoAOD_94XMiniAODv1
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv2_cff import run2_nanoAOD_94XMiniAODv2

from PhysicsTools.PatUtils.L1ECALPrefiringWeightProducer_cff import prefiringweight

def addL1PreFiringEventWeigh(process):
  #NOTE L1PrefiringMaps.root does not include weights for 2018 -> branches not present in the Ntuple
  process.prefiringweight = prefiringweight.clone()
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016:
    modifier.toModify(process.prefiringweight, DataEra = cms.string("2016BtoH"))

  process.l1PreFiringEventWeightTable = cms.EDProducer("GlobalVariablesTableProducer",
    variables = cms.PSet(
      L1PreFiringWeight   = ExtVar(cms.InputTag("prefiringweight:nonPrefiringProb"),
        "double", doc = "L1 pre-firing event correction weight (1-probability)", precision = 8
      ),
      L1PreFiringWeightUp = ExtVar(cms.InputTag("prefiringweight:nonPrefiringProbUp"),
        "double", doc = "L1 pre-firing event correction weight (1-probability), up var.", precision = 8
      ),
      L1PreFiringWeightDn = ExtVar(cms.InputTag("prefiringweight:nonPrefiringProbDown"),
        "double", doc = "L1 pre-firing event correction weight (1-probability), down var.", precision = 8
      ),
    )
  )
  _triggerObjectTables_withL1PreFiring = process.triggerObjectTables.copy()
  _triggerObjectTables_withL1PreFiring.replace(
    process.triggerObjectTable,
    process.prefiringweight + process.l1PreFiringEventWeightTable + process.triggerObjectTable
  )
  for modifier in run2_miniAOD_80XLegacy, run2_nanoAOD_94X2016, run2_nanoAOD_94XMiniAODv1, run2_nanoAOD_94XMiniAODv2:
      modifier.toReplaceWith(process.triggerObjectTables, _triggerObjectTables_withL1PreFiring)

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

  if is_th:
    print("Enabling tH weights")
    process.genWeightsTable.namedWeightIDs = cms.vstring(*tuple(map(lambda x: 'rwgt_%d' % x, range(1, 70))))
    process.genWeightsTable.namedWeightLabels = cms.vstring(*tuple(map(lambda x: 'rwgt_%d' % x, range(1, 70))))

  addJetSubstructureObservables(process)
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = True)
  addLeptonSubtractedAK8Jets(process, runOnMC = is_mc, era = year, useFakeable = False)
  addTauAntiEleMVA2018(process)
  addDeepTau2017v1(process)
  addDPFTau_2016_v0(process)
  addDPFTau_2016_v1(process)
  addL1PreFiringEventWeigh(process)
