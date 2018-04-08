import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import Var, P4Vars

def addJetSubstructureObservables(process, runOnMC):

    process.jetSubstructureSequence = cms.Sequence()

    #----------------------------------------------------------------------------
    # add anti-kT jets for dR = 1.2 (AK12),
    # following instructions posted by Sal on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1792/1.html)
    # CV: "official" version of jetToolbox does not work with nanoAOD,
    #     as the lines https://github.com/cms-jet/JetToolbox/blob/jetToolbox_91X/python/jetToolbox_cff.py#L947-L960
    #     add misconfigured/non-working modules for scheduled execution.
    #     For the time-being, store fixed version of jetToolbox in tthAnalysis/NanoAOD package and use private version instead of "official" one
    from tthAnalysis.NanoAOD.jetToolbox_cff import jetToolbox
    jetToolbox(process, 'ak12', 'jetSequenceAK12', 'out', PUMethod='Puppi', miniAOD=True, runOnMC=runOnMC, addSoftDrop=True, addSoftDropSubjets=True, addNsub=True)
    process.jetSubstructureSequence += process.jetSequenceAK12
    # CV: use jet energy corrections for AK8 Puppi jets
    process.patJetCorrFactorsAK12PFPuppi.payload = cms.string('AK8PFPuppi')
    process.patJetCorrFactorsAK12PFPuppiSoftDrop.payload = cms.string('AK8PFPuppi')
    # CV: disable discriminators that cannot be computed with miniAOD inputs
    for moduleName in [ "patJetsAK12PFPuppi", "patJetsAK12PFPuppiSoftDrop", "patJetsAK12PFPuppiSoftDropSubjets" ]:
        module = getattr(process, moduleName)
        module.discriminatorSources = cms.VInputTag()
    fatJetCollectionAK12 = 'packedPatJetsAK12PFPuppiSoftDrop'
    subJetCollectionAK12 = 'selectedPatJetsAK12PFPuppiSoftDropPacked:SubJets'
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # CV: add 'patJetPartons' module to 'genParticleSequence' (which runs at beginning of event processing),
    #     to avoid run-time exception of type:
    #
    #       ----- Begin Fatal Exception 22-Feb-2018 10:16:02 EET-----------------------
    #       An exception of category 'ScheduleExecutionFailure' occurred while
    #          [0] Calling beginJob
    #       Exception Message:
    #       Unrunnable schedule
    #       Module run order problem found:
    #       ...
    #        Running in the threaded framework would lead to indeterminate results.
    #        Please change order of modules in mentioned Path(s) to avoid inconsistent module ordering.
    #       ----- End Fatal Exception -------------------------------------------------
    if hasattr(process, "patJetPartons") and hasattr(process, "genParticleSequence") and runOnMC:
        process.genParticleSequence += process.patJetPartons
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add PF jet ID flags and jet energy corrections for AK12 pat::Jet collection,
    # following what is done for AK8 pat::Jets in https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/jets_cff.py
    process.tightJetIdAK12 = process.tightJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetSubstructureSequence += process.tightJetIdAK12
    process.tightJetIdLepVetoAK12 = process.tightJetIdLepVetoAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetSubstructureSequence += process.tightJetIdLepVetoAK12
    process.jetsAK12WithUserData = process.slimmedJetsAK8WithUserData.clone(
        src = cms.InputTag(fatJetCollectionAK12),
        userInts = cms.PSet(
            tightId = cms.InputTag("tightJetIdAK12"),
            tightIdLepVeto = cms.InputTag("tightJetIdLepVetoAK12"),
        )
    )
    process.jetSubstructureSequence += process.jetsAK12WithUserData
    process.jetCorrFactorsAK12 = process.jetCorrFactorsAK8.clone(
        src = cms.InputTag('jetsAK12WithUserData')
    )
    process.jetSubstructureSequence += process.jetCorrFactorsAK12
    process.updatedJetsAK12 = process.updatedJetsAK8.clone(
        jetSource = cms.InputTag('jetsAK12WithUserData'),
        jetCorrFactorsSource = cms.VInputTag(cms.InputTag('jetCorrFactorsAK12'))
    )
    process.jetSubstructureSequence += process.updatedJetsAK12

    process.selectedJetsAK12 = cms.EDFilter("PATJetSelector",
        src      = cms.InputTag("updatedJetsAK12"),
        cut      = cms.string("pt > 130 && abs(eta) < 2.4"),
        cutLoose = cms.string(""),
        nLoose   = cms.uint32(0),
        filter   = cms.bool(False),
    )
    process.jetSubstructureSequence += process.selectedJetsAK12
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # compute edm::ValueMaps with Qjets volatility (arXiv:1001.5027),
    # following instructions posted by Andrea Marini on JetMET Hypernews (https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1790/1.html)
    if not hasattr(process, "RandomNumberGeneratorService"):
        process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService")
    process.RandomNumberGeneratorService.QJetsAdderCA8 = cms.PSet(initialSeed = cms.untracked.uint32(7))
    process.RandomNumberGeneratorService.QJetsAdderAK8 = cms.PSet(initialSeed = cms.untracked.uint32(31))
    process.RandomNumberGeneratorService.QJetsAdderAK12 = cms.PSet(initialSeed = cms.untracked.uint32(53))
    process.RandomNumberGeneratorService.QJetsAdderCA15 = cms.PSet(initialSeed = cms.untracked.uint32(76))
    from RecoJets.JetProducers.qjetsadder_cfi import QJetsAdder
    process.QJetsAdderAK12 = QJetsAdder.clone(
        src = cms.InputTag('selectedJetsAK12'),
        jetRad = cms.double(1.2),
        jetAlgo = cms.string("AK")
    )
    process.jetSubstructureSequence += process.QJetsAdderAK12
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility as userFloats to AK12 pat::Jet collection
    process.extendedFatJetsAK12 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('selectedJetsAK12'),
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
                src = cms.InputTag('QJetsAdderAK12:QjetsVolatility')
            )
        )
    )
    process.jetSubstructureSequence += process.extendedFatJetsAK12
    process.extendedSubJetsAK12 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag(subJetCollectionAK12),
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
    process.jetSubstructureSequence += process.extendedSubJetsAK12
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility to nanoAOD
    process.fatJetAK12Table = process.fatJetTable.clone(
        src = cms.InputTag('extendedFatJetsAK12'),
        cut = cms.string("pt > 100"),
        name = cms.string("FatJetAK12"),
        doc = cms.string("ak12 fat jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10),
            QjetVolatility = Var("userFloat('QjetVolatility')",float, doc="Qjets volatility, computed according to arXiv:1201.1914",precision=10),
            msoftdrop = Var("userFloat('ak12PFJetsPuppiSoftDropMass')",float, doc="Corrected soft drop mass with PUPPI",precision=10),
            subJetIdx1 = Var("?subjets('SoftDrop').size()>0?subjets('SoftDrop').at(0).key():-1", int, doc="index of first subjet"),
            subJetIdx2 = Var("?subjets('SoftDrop').size()>1?subjets('SoftDrop').at(1).key():-1", int, doc="index of second subjet"),
            tau1 = Var("userFloat('NjettinessAK12Puppi:tau1')",float, doc="Nsubjettiness (1 axis)",precision=10),
            tau2 = Var("userFloat('NjettinessAK12Puppi:tau2')",float, doc="Nsubjettiness (2 axis)",precision=10),
            tau3 = Var("userFloat('NjettinessAK12Puppi:tau3')",float, doc="Nsubjettiness (3 axis)",precision=10),
            tau4 = Var("userFloat('NjettinessAK12Puppi:tau4')",float, doc="Nsubjettiness (4 axis)",precision=10)
        )
    )
    process.jetSubstructureSequence += process.fatJetAK12Table
    process.subJetAK12Table = process.subJetTable.clone(
        src = cms.InputTag('extendedSubJetsAK12'),
        cut = cms.string(""),
        name = cms.string("SubJetAK12"),
        doc = cms.string("ak12 sub-jets for boosted analysis"),
        variables = cms.PSet(P4Vars,
            jetCharge = Var("userFloat('jetCharge')",float, doc="jet charge, computed according to JME-13-006",precision=10),
            pullEta = Var("userFloat('pull_dEta')",float, doc="eta component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullPhi = Var("userFloat('pull_dPhi')",float, doc="phi component of pull vector, computed according to arXiv:1001.5027",precision=10),
            pullMag = Var("userFloat('pull_dR')",float, doc="magnitude of pull vector, computed according to arXiv:1001.5027",precision=10)
        )
    )
    process.jetSubstructureSequence += process.subJetAK12Table
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # CV: switch to unscheduled mode, as the jetToolbox and PAT tools do not support scheduled mode - it's a mess !!
    #process.nanoSequence += process.jetSubstructureSequence
    process.jetSubstructureTask = cms.Task()
    for moduleName in process.jetSubstructureSequence.moduleNames():
        module = getattr(process, moduleName)
        process.jetSubstructureTask.add(module)
    process.jetSubstructureTables = cms.Sequence(process.fatJetAK12Table + process.subJetAK12Table)
    # CV: add tasks to sequence,
    #     as described on this twiki: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Module_sequences
    #    (some modules are contained in 'jetSubstructureTask' and some are contained in 'patAlgosToolsTask' - it's again a mess !!)
    process.jetSubstructureTables.associate(process.jetSubstructureTask)
    process.jetSubstructureTables.associate(process.patAlgosToolsTask)
    process.nanoSequence += process.jetSubstructureTables
    #----------------------------------------------------------------------------

    #----------------------------------------------------------------------------
    # add jet charge and pull as userFloats to AK4 pat::Jet collection
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
