import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var
from PhysicsTools.NanoAOD.taus_cff import _tauIdWPMask, _tauId5WPMask

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv1_cff import run2_nanoAOD_94XMiniAODv1
from Configuration.Eras.Modifier_run2_nanoAOD_92X_cff import run2_nanoAOD_92X

## Raw
from RecoTauTag.RecoTau.PATTauDiscriminationAgainstElectronMVA6_cfi import patTauDiscriminationAgainstElectronMVA6
from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants

## anti-e 2018 WPs
from RecoTauTag.RecoTau.PATTauDiscriminantCutMultiplexer_cfi import patTauDiscriminantCutMultiplexer

import re

#NOTE Implements
# - tau DNN from https://github.com/cms-sw/cmssw/blob/master/RecoTauTag/RecoTau/python/tools/runTauIdMVA.py
# - anti-e MVA from https://github.com/cms-nanoAOD/cmssw/pull/276
#
# Documentation:
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Running_of_the_DNN_based_tau_ID
# https://twiki.cern.ch/twiki/bin/view/CMS/TauIDRecommendation13TeV

#TODO
# - consider different tau collections other than slimmedTaus (e.g. ("linkedObjects","taus"))
# - consider different electron collections other than slimmedElectrons (e.g. slimmedElectronsUpdated, slimmedElectronsWithUserData, ("linkedObjects","electrons"))
# - consdier different muon collections other than slimmedMuons (e.g. slimmedMuonsUpdated, slimmedMuonsWithUserData, ("linkedObjects","muons"))
# - consider different jet collections other than slimmedJets (e.g. slimmedJetsWithUserData, updatedJets, ("linkedObjects","jets"))

def _tauId8WPMask(pattern,doc):
  return _tauIdWPMask(
    pattern,
    choices = ("VVVLoose", "VVLoose", "VLoose", "Loose", "Medium", "Tight", "VTight", "VVTight"),
    doc = doc
  )

def getDpfTauVersion(file_name):
  """returns the DNN version. File name should contain a version label with data takig year (2011-2, 2015-8) and \
     version number (vX), e.g. 2017v0, in general the following format: {year}v{version}"""
  version_search = re.search('201[125678]v([0-9]+)[\._]', file_name)
  if not version_search:
    raise RuntimeError(
      'File "%s" has an invalid name pattern, should be in the format "{year}v{version}". Unable to extract version number.' % \
      file_name
    )
  version = version_search.group(1)
  return int(version)

def addToTauTable(process, vars):
  tau_variables = process.tauTable.variables.clone()
  tau_variables_copy = tau_variables.clone()

  for varItem in vars:
    varName, varValue = varItem
    setattr(tau_variables, varName, varValue)
  process.tauTable.variables = tau_variables

  for modifier in run2_nanoAOD_94XMiniAODv1, run2_nanoAOD_92X:
    modifier.toModify(process.tauTable, variables = tau_variables_copy)
  run2_miniAOD_80XLegacy.toModify(process.tauTable, variables = tau_variables_copy)

def processDeepProducer(process, producer_name, workingPoints_):
  prefix = producer_name[0].upper() + producer_name[1:]
  for target, points in workingPoints_.iteritems():
    cuts = cms.PSet()
    setattr(
      process.slimmedTausUpdated.tauIDSources,
      'by{}VS{}raw'.format(prefix, target),
      cms.InputTag(producer_name, 'VS{}'.format(target))
    )
    for point, cut in points.iteritems():
      setattr(cuts, point, cms.string(str(cut)))
      setattr(
        process.slimmedTausUpdated.tauIDSources,
        'by{}{}VS{}'.format(point, prefix, target),
        cms.InputTag(producer_name, 'VS{}{}'.format(target, point))
      )
    setattr(getattr(process, producer_name), 'VS{}WP'.format(target), cuts)

def addDeepTau2017v1(process):
  # https://github.com/cms-sw/cmssw/blob/fbfd5f2bbaa7f182d3487780fec554c48b10df2e/RecoTauTag/RecoTau/python/tools/runTauIdMVA.py#L602-L650
  print("Adding DeepTau IDs")
  workingPoints_ = {
    "e": {
      "VVVLoose" : 0.96424,
      "VVLoose"  : 0.98992,
      "VLoose"   : 0.99574,
      "Loose"    : 0.99831,
      "Medium"   : 0.99868,
      "Tight"    : 0.99898,
      "VTight"   : 0.99911,
      "VVTight"  : 0.99918,
    },
    "mu": {
      "VVVLoose" : 0.959619,
      "VVLoose"  : 0.997687,
      "VLoose"   : 0.999392,
      "Loose"    : 0.999755,
      "Medium"   : 0.999854,
      "Tight"    : 0.999886,
      "VTight"   : 0.999944,
      "VVTight"  : 0.9999971,
    },

    "jet": {
      "VVVLoose"  : 0.5329,
      "VVLoose"   : 0.7645,
      "VLoose"    : 0.8623,
      "Loose"     : 0.9140,
      "Medium"    : 0.9464,
      "Tight"     : 0.9635,
      "VTight"    : 0.9760,
      "VVTight"   : 0.9859,
    },
  }
  file_name = 'RecoTauTag/TrainingFiles/data/DeepTauId/deepTau_2017v1_20L1024N_quantized.pb'
  process.deepTau2017v1 = cms.EDProducer("DeepTauId",
    electrons              = cms.InputTag('slimmedElectrons'),
    muons                  = cms.InputTag('slimmedMuons'),
    taus                   = cms.InputTag('slimmedTaus'),
    graph_file             = cms.string(file_name),
    mem_mapped             = cms.bool(False),
  )

  processDeepProducer(process, 'deepTau2017v1', workingPoints_)
  process.patTauMVAIDsSeq.insert(
    process.patTauMVAIDsSeq.index(process.slimmedTausUpdated),
    process.deepTau2017v1
  )

  deepTau2017v1Vars = []
  for obj in workingPoints_:
    assert(len(workingPoints_[obj]) == 8)
    deepTau2017v1Vars.extend([
      ("rawDeepTau2017v1VS{}".format(obj), Var(
        "tauID('byDeepTau2017v1VS{}raw')".format(obj),
        float, doc = "Anti-{} DNN discriminator raw output (2018)", precision = 10)
      ),
      ("idDeepTau2017v1VS{}".format(obj), _tauId8WPMask(
          "by%sDeepTau2017v1VS{}".format(obj),
          doc = "Anti-{} DNN discriminator (2018)".format(obj)
        )
      ),
    ])
  addToTauTable(process, deepTau2017v1Vars)

def addDPFTau_2016_v0(process):
  # https://github.com/cms-sw/cmssw/blob/fbfd5f2bbaa7f182d3487780fec554c48b10df2e/RecoTauTag/RecoTau/python/tools/runTauIdMVA.py#L652-L682
  print("Adding DPFTau isolation (v0)")

  workingPoints_ = {
    "all": {
      "Tight" : "if(decayMode == 0) return (0.898328 - 0.000160992 * pt);" + \
                "if(decayMode == 1) return (0.910138 - 0.000229923 * pt);" + \
                "if(decayMode == 10) return (0.873958 - 0.0002328 * pt);" + \
                "return 99.0;"
    }
  }
  file_name = 'RecoTauTag/TrainingFiles/data/DPFTauId/DPFIsolation_2017v0_quantized.pb'
  process.dpfTau2016v0 = cms.EDProducer("DPFIsolation",
      pfcands     = cms.InputTag('packedPFCandidates'),
      taus        = cms.InputTag('slimmedTaus'),
      vertices    = cms.InputTag('offlineSlimmedPrimaryVertices'),
      graph_file  = cms.string(file_name),
      version     = cms.uint32(getDpfTauVersion(file_name)),
      mem_mapped  = cms.bool(False),
  )

  processDeepProducer(process, 'dpfTau2016v0', workingPoints_)
  process.patTauMVAIDsSeq.insert(
    process.patTauMVAIDsSeq.index(process.slimmedTausUpdated),
    process.dpfTau2016v0
  )

  dpfTau2016v0Vars = [
    ("rawDpfTau2016v0VSall", Var(
        "tauID('byDpfTau2016v0VSallraw')", float, doc = "DPFTau vs all (v0) raw output", precision = 10
      )
    ),
    ("idDpfTau2016v0VSall", Var(
        "1 * tauID('byTightDpfTau2016v0VSall')", "uint8", doc = "DPFTau vs all (v0)"
      )
    ),
  ]
  addToTauTable(process, dpfTau2016v0Vars)

def addDPFTau_2016_v1(process):
  # https://github.com/cms-sw/cmssw/blob/fbfd5f2bbaa7f182d3487780fec554c48b10df2e/RecoTauTag/RecoTau/python/tools/runTauIdMVA.py#L685-L707
  print("Adding DPFTau isolation (v1)")
  print("WARNING: WPs are not defined for DPFTau_2016_v1")
  print("WARNING: The score of DPFTau_2016_v1 is inverted: i.e. for Sig->0, for Bkg->1 with -1 for undefined input (preselection not passed).")

  workingPoints_ = {
      "all": {"Tight" : 0.123} #FIXME: define WP
  }

  file_name = 'RecoTauTag/TrainingFiles/data/DPFTauId/DPFIsolation_2017v1_quantized.pb'
  process.dpfTau2016v1 = cms.EDProducer("DPFIsolation",
    pfcands     = cms.InputTag('packedPFCandidates'),
    taus        = cms.InputTag('slimmedTaus'),
    vertices    = cms.InputTag('offlineSlimmedPrimaryVertices'),
    graph_file  = cms.string(file_name),
    version     = cms.uint32(getDpfTauVersion(file_name)),
    mem_mapped  = cms.bool(False),
  )

  processDeepProducer(process, 'dpfTau2016v1', workingPoints_)
  process.patTauMVAIDsSeq.insert(
    process.patTauMVAIDsSeq.index(process.slimmedTausUpdated),
    process.dpfTau2016v1
  )
  dpfTau2016v1Vars = [
    ("rawDpfTau2016v1VSall", Var(
        "tauID('byDpfTau2016v1VSallraw')", float, doc = "DPFTau vs all (v1) raw output", precision = 10
      )
    ),
  ]
  addToTauTable(process, dpfTau2016v1Vars)

def addTauAntiEleMVA2018(process):
  # https://github.com/cms-nanoAOD/cmssw/pull/276

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

  antiEleVars = [
    ("rawAntiEle2018", Var(
        "tauID('againstElectronMVA6Raw2018')",
        float, doc = "Anti-electron MVA discriminator V6 raw output discriminator (2018)", precision = 10
      )
    ),
    ("rawAntiEleCat2018", Var(
        "tauID('againstElectronMVA6category2018')",
        int, doc = "Anti-electron MVA discriminator V6 category (2018)"
      )
    ),
    ("idAntiEle2018", _tauId5WPMask(
        "againstElectron%sMVA62018", doc = "Anti-electron MVA discriminator V6 (2018)"
      )
    ),
  ]
  addToTauTable(process, antiEleVars)
