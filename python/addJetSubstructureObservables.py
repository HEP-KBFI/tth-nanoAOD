import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy

def addJetSubstructureObservables(process, runOnMC):

    jetSubstructureSequence = cms.Sequence()

    #----------------------------------------------------------------------------
    # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
    # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
    if not hasattr(process, "RandomNumberGeneratorService"):
        process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
    process.RandomNumberGeneratorService.QJetsAdderAK8 = cms.PSet(initialSeed = cms.untracked.uint32(31))
    from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
    process.QJetsAdderAK8 = QJetsAdder.clone(
        src = cms.InputTag('updatedJetsAK8'),
        jetRad = cms.double(0.8),
        jetAlgo = cms.string("AK")
    )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility to AK8 pat::Jet collection
    process.extendedFatJetsAK8 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('updatedJetsAK8'),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            ),
            cms.PSet(
                pluginType = cms.string("JetValueMapPlugin"),
                label = cms.string("QjetVolatility"),
                overwrite = cms.bool(False),
                src = cms.InputTag('QJetsAdderAK8:QjetsVolatility')
            )
        )
    )    
    process.finalJetsAK8.src = cms.InputTag('extendedFatJetsAK8')
    # CV: reduce pT cut on reconstructed and generator-level AK8 jets to 80 GeV
    #    (to allow for pT > 100 GeV cut to be applied on analysis level, while leaving some "room" for JES and JER uncertainties to be applied)
    process.finalJetsAK8.cut = cms.string("pt > 80")
    process.genJetAK8Table.cut = cms.string("pt > 80")
    process.genJetAK8FlavourTable.cut = cms.string("pt > 80")
    process.fatJetTable.cut = cms.string("pt > 80")
    process.fatJetTable.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.fatJetTable.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTable.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTable.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.fatJetTable.variables.QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10)
       
    process.extendedSubJetsAK8 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag("slimmedJetsAK8PFPuppiSoftDropPacked","SubJets"),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            )
        )
    )
    process.subJetTable.src = cms.InputTag('extendedSubJetsAK8')
    process.subJetTable.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.subJetTable.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.subJetTable.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.subJetTable.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetSequence.replace(process.updatedJetsAK8, process.updatedJetsAK8 + process.QJetsAdderAK8 + process.extendedFatJetsAK8 + process.extendedSubJetsAK8)
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge as userFloat to AK4 pat::Jet collection
    process.extendedJets = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('updatedJets'),
        plugins = cms.VPSet(
            cms.PSet(
                pluginType = cms.string("JetChargePlugin"),
                label = cms.string("jetCharge"),
                overwrite = cms.bool(False),
                kappa = cms.double(1.)
            ),
            cms.PSet(
                pluginType = cms.string("JetPullPlugin"),
                label = cms.string("pull"),
                overwrite = cms.bool(False)
            )
        )
    )
    process.jetSequence.replace(process.updatedJets, process.updatedJets + process.extendedJets)
    process.finalJets.src = cms.InputTag('extendedJets')
    process.jetTable.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.jetTable.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    #----------------------------------------------------------------------------
