import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars

def addJetSubstructureObservables(process, addQJets = False):

    if addQJets:
        print("Adding Qjet volatility to %s" % process.fatJetTable.name.value())
    else:
        print("NOT adding Qjet volatility to %s" % process.fatJetTable.name.value())

    #----------------------------------------------------------------------------
    # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
    # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
    if addQJets:
        from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
        if not hasattr(process, "RandomNumberGeneratorService"):
            process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
        process.RandomNumberGeneratorService.QJetsAdderAK8 = cms.PSet(initialSeed = cms.untracked.uint32(31))
        process.QJetsAdderAK8 = QJetsAdder.clone(
            src = cms.InputTag('updatedJetsAK8'),
            jetRad = cms.double(0.8),
            jetAlgo = cms.string("AK")
        )
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    process.jetAK8SubStructureVars = cms.EDProducer("JetSubstructureObservableProducer",
        src = cms.InputTag("updatedJetsAK8"),
        kappa = cms.double(1.),
    )
    process.updatedJetsAK8WithUserData.userFloats.jetCharge = cms.InputTag("jetAK8SubStructureVars:jetCharge")
    process.updatedJetsAK8WithUserData.userFloats.pull_dEta = cms.InputTag("jetAK8SubStructureVars:pullDEta")
    process.updatedJetsAK8WithUserData.userFloats.pull_dPhi = cms.InputTag("jetAK8SubStructureVars:pullDPhi")
    process.updatedJetsAK8WithUserData.userFloats.pull_dR = cms.InputTag("jetAK8SubStructureVars:pullDR")
    if addQJets:
        process.updatedJetsAK8WithUserData.userFloats.QjetVolatility = cms.InputTag("QJetsAdderAK8:QjetsVolatility")

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
    if addQJets:
        process.fatJetTable.variables.QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10)

    process.jetSequence.replace(process.updatedJetsAK8WithUserData, process.jetAK8SubStructureVars + process.updatedJetsAK8WithUserData)
    if addQJets:
        process.jetSequence.replace(process.updatedJetsAK8WithUserData, process.QJetsAdderAK8 + process.updatedJetsAK8WithUserData)
    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    process.subJetSubStructureVars = cms.EDProducer("JetSubstructureObservableProducer",
        src = cms.InputTag("slimmedJetsAK8PFPuppiSoftDropPacked","SubJets"),
        kappa = cms.double(1.),
    )
    process.subJetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
        src = cms.InputTag("slimmedJetsAK8PFPuppiSoftDropPacked", "SubJets"),
        userFloats = cms.PSet(
            jetCharge = cms.InputTag("subJetSubStructureVars:jetCharge"),
            pull_dEta = cms.InputTag("subJetSubStructureVars:pullDEta"),
            pull_dPhi = cms.InputTag("subJetSubStructureVars:pullDPhi"),
            pull_dR   = cms.InputTag("subJetSubStructureVars:pullDR"),
        ),
        userInts = cms.PSet(),
    )
    process.subJetTable.src = cms.InputTag('subJetsWithUserData')
    process.subJetTable.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.subJetTable.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.subJetTable.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.subJetTable.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetSequence += cms.Sequence(process.subJetSubStructureVars + process.subJetsWithUserData)
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    process.jetSubStructureVars = cms.EDProducer("JetSubstructureObservableProducer",
        src = cms.InputTag("updatedJets"),
        kappa = cms.double(1.),
    )
    process.updatedJetsWithUserData.userFloats.jetCharge = cms.InputTag("jetSubStructureVars:jetCharge")
    process.updatedJetsWithUserData.userFloats.pull_dEta = cms.InputTag("jetSubStructureVars:pullDEta")
    process.updatedJetsWithUserData.userFloats.pull_dPhi = cms.InputTag("jetSubStructureVars:pullDPhi")
    process.updatedJetsWithUserData.userFloats.pull_dR = cms.InputTag("jetSubStructureVars:pullDR")

    process.jetTable.variables.jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10)
    process.jetTable.variables.pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10)
    process.jetTable.variables.pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
    
    process.jetSequence.replace(process.updatedJetsWithUserData, process.jetSubStructureVars + process.updatedJetsWithUserData)
    #----------------------------------------------------------------------------
