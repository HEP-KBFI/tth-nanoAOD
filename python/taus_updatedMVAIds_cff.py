import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var
from PhysicsTools.NanoAOD.taus_cff import _tauIdWPMask

from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy
from Configuration.Eras.Modifier_run2_nanoAOD_94X2016_cff import run2_nanoAOD_94X2016
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv1_cff import run2_nanoAOD_94XMiniAODv1
from Configuration.Eras.Modifier_run2_nanoAOD_94XMiniAODv2_cff import run2_nanoAOD_94XMiniAODv2
from Configuration.Eras.Modifier_run2_nanoAOD_102Xv1_cff import run2_nanoAOD_102Xv1

import re

def _tauId4WPMask(pattern,doc):
  return _tauIdWPMask(
    pattern,
    choices = ("VLoose", "Loose", "Medium", "Tight"),
    doc = doc
  )

def _tauId8WPMask(pattern,doc):
  return _tauIdWPMask(
    pattern,
    choices = ("VVVLoose", "VVLoose", "VLoose", "Loose", "Medium", "Tight", "VTight", "VVTight"),
    doc = doc
  )

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

def getDeepTauVersion(file_name):
  """returns the DeepTau year, version, subversion. File name should contain a version label with data takig year \
  (2011-2, 2015-8), version number (vX) and subversion (pX), e.g. 2017v0p6, in general the following format: \
  {year}v{version}p{subversion}"""
  version_search = re.search('(201[125678])v([0-9]+)(p[0-9]+|)[\._]', file_name)
  if not version_search:
    raise RuntimeError('File "%s" has an invalid name pattern, should be in the format "{year}v{version}p{subversion}" '
                       'Unable to extract version number.' % file_name)
  year = version_search.group(1)
  version = version_search.group(2)
  subversion = version_search.group(3)
  if len(subversion) > 0:
    subversion = subversion[1:]
  else:
    subversion = 0
  return int(year), int(version), int(subversion)

def addToTauTable(process, vars):
  tau_variables = process.tauTable.variables.clone()

  for varItem in vars:
    varName, varValue = varItem
    setattr(tau_variables, varName, varValue)

  for modifier in run2_nanoAOD_94X2016, run2_nanoAOD_94XMiniAODv2, run2_nanoAOD_102Xv1:
    modifier.toModify(
      process.tauTable, variables = tau_variables
    )

def addDeepTau2017v2(process):
  print ("Adding DeepTau IDs")

  workingPoints_ = {
    "e": {
      "VVVLoose": 0.0630386,
      "VVLoose": 0.1686942,
      "VLoose": 0.3628130,
      "Loose": 0.6815435,
      "Medium": 0.8847544,
      "Tight": 0.9675541,
      "VTight": 0.9859251,
      "VVTight": 0.9928449,
    },
    "mu": {
      "VLoose": 0.1058354,
      "Loose": 0.2158633,
      "Medium": 0.5551894,
      "Tight": 0.8754835,
    },
    "jet": {
      "VVVLoose": 0.2599605,
      "VVLoose": 0.4249705,
      "VLoose": 0.5983682,
      "Loose": 0.7848675,
      "Medium": 0.8834768,
      "Tight": 0.9308689,
      "VTight": 0.9573137,
      "VVTight": 0.9733927,
    },
  }
  file_name = 'tthAnalysis/NanoAOD/data/DeepTauId/deepTau_2017v2p6_e6.pb'
  process.deepTau2017v2 = cms.EDProducer("DeepTauId",
    electrons              = cms.InputTag('slimmedElectrons'),
    muons                  = cms.InputTag('slimmedMuons'),
    taus                   = cms.InputTag('slimmedTaus'),
    pfcands                = cms.InputTag('packedPFCandidates'),
    vertices               = cms.InputTag('offlineSlimmedPrimaryVertices'),
    rho                    = cms.InputTag('fixedGridRhoAll'),
    graph_file             = cms.string(file_name),
    mem_mapped             = cms.bool(True),
    version                = cms.uint32(getDeepTauVersion(file_name)[1]),
    debug_level            = cms.int32(0),
  )

  processDeepProducer(process, 'deepTau2017v2', workingPoints_)

  for modifier in run2_nanoAOD_94X2016, run2_nanoAOD_94XMiniAODv2, run2_nanoAOD_102Xv1:
    patTauMVAIDsSeq_copy = process.patTauMVAIDsSeq.copy()
    patTauMVAIDsSeq_copy.insert(
      patTauMVAIDsSeq_copy.index(process.slimmedTausUpdated),
      process.deepTau2017v2
    )
    modifier.toReplaceWith(process.patTauMVAIDsSeq, patTauMVAIDsSeq_copy)

  deepTau2017v2Vars = []
  for obj in workingPoints_:
    if len(workingPoints_[obj]) == 8:
      tauIdWPMask = _tauId8WPMask
    elif len(workingPoints_[obj]) == 4:
      tauIdWPMask = _tauId4WPMask
    else:
      raise RuntimeError("Unexpected number of WPs: %d" % len(workingPoints_[obj]))
    assert(tauIdWPMask)

    deepTau2017v2Vars.extend([
      ("rawDeepTau2017v2VS{}".format(obj), Var(
        "tauID('byDeepTau2017v2VS{}raw')".format(obj),
        float, doc = "Anti-{} DNN discriminator raw output (v2)", precision = 10)
      ),
      ("idDeepTau2017v2VS{}".format(obj), tauIdWPMask(
          "by%sDeepTau2017v2VS{}".format(obj),
          doc = "Anti-{} DNN discriminator (v2)".format(obj)
        )
      ),
    ])
  addToTauTable(process, deepTau2017v2Vars)

  process.finalTaus.cut = cms.string(
    "pt > 18 && tauID('decayModeFindingNewDMs') && ("
      "tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') || "
      "tauID('byVLooseIsolationMVArun2v1DBoldDMwLT2015') || "
      "tauID('byVLooseIsolationMVArun2v1DBnewDMwLT') || "
      "tauID('byVLooseIsolationMVArun2v1DBdR03oldDMwLT') || "
      "tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT') || "
      "tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT2017v2') || "
      "tauID('byVVLooseIsolationMVArun2v1DBnewDMwLT2017v2') || "
      "tauID('byVVLooseIsolationMVArun2v1DBdR03oldDMwLT2017v2') ||"
      "tauID('byVVVLooseDeepTau2017v2VSe') ||"
      "tauID('byVLooseDeepTau2017v2VSmu') ||"
      "tauID('byVVVLooseDeepTau2017v2VSjet')"
    ")"
  )
  run2_nanoAOD_94XMiniAODv1.toModify(
    process.finalTaus,
    cut = cms.string(
      "pt > 18 && tauID('decayModeFindingNewDMs') && ("
        "tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') || "
        "tauID('byVLooseIsolationMVArun2v1DBoldDMwLT') || "
        "tauID('byVLooseIsolationMVArun2v1DBnewDMwLT') || "
        "tauID('byVLooseIsolationMVArun2v1DBdR03oldDMwLT') || "
        "tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT2017v1') || "
        "tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT2017v2') || "
        "tauID('byVVLooseIsolationMVArun2v1DBnewDMwLT2017v2') || "
        "tauID('byVVLooseIsolationMVArun2v1DBdR03oldDMwLT2017v2')"
      ")"
    )
  )
  run2_miniAOD_80XLegacy.toModify(
    process.finalTaus,
    cuts = cms.string(
      "pt > 18 && tauID('decayModeFindingNewDMs') && ("
        "tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') || "
        "tauID('byVLooseIsolationMVArun2v1DBoldDMwLT') || "
        "tauID('byVLooseIsolationMVArun2v1DBnewDMwLT') || "
        "tauID('byVLooseIsolationMVArun2v1DBdR03oldDMwLT')"
      ")"
    )
  )
