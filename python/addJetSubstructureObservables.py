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
    if hasattr(process, "patJetPartons"):
        process.jetSubstructureSequence += process.patJetPartons
    # CV: use jet energy corrections for AK8 Puppi jets
    process.patJetCorrFactorsAK12PFPuppi.payload = cms.string('AK8PFPuppi')   
    process.patJetCorrFactorsAK12PFPuppiSoftDrop.payload = cms.string('AK8PFPuppi')
    # CV: disable discriminators that cannot be computed with miniAOD inputs
    for moduleName in [ "patJetsAK12PFPuppi", "patJetsAK12PFPuppiSoftDrop", "patJetsAK12PFPuppiSoftDropSubjets" ]:
        module = getattr(process, moduleName)
        module.discriminatorSources = cms.VInputTag()
    ##fatJetCollectionAK12 = 'patJetsAK12PFPuppi'
    ##fatJetCollectionAK12 = 'selectedPatJetsAK12PFPuppiSoftDropPacked
    fatJetCollectionAK12 = 'packedPatJetsAK12PFPuppiSoftDrop'
    subJetCollectionAK12 = 'selectedPatJetsAK12PFPuppiSoftDropPacked:SubJets'
    #----------------------------------------------------------------------------

##     #----------------------------------------------------------------------------
##     # add softdrop mass
##     # (taken from https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/python/slimming/applySubstructure_cff.py#L201-L204)
##     from RecoJets.JetProducers.ak8PFJetsPuppi_groomingValueMaps_cfi import ak8PFJetsPuppiSoftDropMass
##     ak12PFJetsPuppiSoftDropMass = ak8PFJetsPuppiSoftDropMass.clone(
##         src = cms.InputTag("ak12PFJetsPuppi"),
##         matched = cms.InputTag("ak12PFJetsPuppiSoftDrop"),                                         
##         distMax = cms.double(1.2)
##     )
##     getattr(process,"patJetsAK12PFPuppiSoftdrop").userData.userFloats.src += ['ak8PFJetsPuppiSoftDropMass'+postfix]
##     process.jetSubstructureSequence += process.ak12PFJetsPuppiSoftDropMass
##     #----------------------------------------------------------------------------

##     #----------------------------------------------------------------------------
##     # add N0-subjettiness
##     # (taken from https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatAlgos/python/slimming/applySubstructure_cff.py#L214-L218)

    
##     addToProcessAndTask('ak12PFJetsPuppiSoftDropMass', ak12PFJetsPuppiSoftDropMass, process, task)
    
## ## now add AK8 groomed masses and ECF
## 0202     from RecoJets.JetProducers.ak8PFJetsPuppi_groomingValueMaps_cfi import ak8PFJetsPuppiSoftDropMass
## 0203     addToProcessAndTask('ak8PFJetsPuppiSoftDropMass'+postfix, ak8PFJetsPuppiSoftDropMass.clone(), process, task)
## 0204     getattr(process,"patJetsAK8Puppi"+postfix).userData.userFloats.src += ['ak8PFJetsPuppiSoftDropMass'+postfix]
## 0205     getattr(process,"patJetsAK8Puppi"+postfix).addTagInfos = cms.bool(False)
## 0206     getattr(process,"patJetsAK8Puppi"+postfix).userData.userFloats.src += [
## 0207         cms.InputTag('ak8PFJetsPuppiSoftDropValueMap'+postfix,'nb1AK8PuppiSoftDropN2'),
## 0208         cms.InputTag('ak8PFJetsPuppiSoftDropValueMap'+postfix,'nb1AK8PuppiSoftDropN3'),
## 0209         cms.InputTag('ak8PFJetsPuppiSoftDropValueMap'+postfix,'nb2AK8PuppiSoftDropN2'),
## 0210         cms.InputTag('ak8PFJetsPuppiSoftDropValueMap'+postfix,'nb2AK8PuppiSoftDropN3'),
## 0211         ]
## 0212 
## 0213 
## 0214     # add PUPPI Njetiness
## 0215     addToProcessAndTask('NjettinessAK8Puppi'+postfix, process.Njettiness.clone(), process, task)
## 0216     getattr(process,"NjettinessAK8Puppi"+postfix).src = cms.InputTag("ak8PFJetsPuppi"+postfix)
## 0217     getattr(process,"NjettinessAK8Puppi").cone = cms.double(0.8)
## 0218     getattr(process,"patJetsAK8Puppi").userData.userFloats.src += ['NjettinessAK8Puppi'+postfix+':tau1','NjettinessAK8Puppi'+postfix+':tau2','NjettinessAK8Puppi'+postfix+':tau3','NjettinessAK8Puppi'+postfix+':tau4']
## 0219 
    
##  from RecoJets.JetProducers.ak8PFJetsCHS_groomingValueMaps_cfi import ak8PFJetsCHSPrunedMass, ak8PFJetsCHSTrimmedMass, ak8PFJetsCHSFilteredMass, ak8PFJetsCHSSoftDropMass
## 0055     addToProcessAndTask('ak8PFJetsCHSPrunedMass'+postfix, ak8PFJetsCHSPrunedMass.clone(), process, task)
## 0056     addToProcessAndTask('ak8PFJetsCHSTrimmedMass'+postfix, ak8PFJetsCHSTrimmedMass.clone(), process, task)
## 0057     addToProcessAndTask('ak8PFJetsCHSFilteredMass'+postfix, ak8PFJetsCHSFilteredMass.clone(), process, task)
## 0058     addToProcessAndTask('ak8PFJetsCHSSoftDropMass'+postfix, ak8PFJetsCHSSoftDropMass.clone(), process, task)
## 0059 
## 0060     getattr(process,"patJetsAK8").userData.userFloats.src += ['ak8PFJetsCHSPrunedMass'+postfix,'ak8PFJetsCHSSoftDropMass'+postfix]  
## 0061     getattr(process,"patJetsAK8").addTagInfos = cms.bool(False)
## 0062 
## 0063     # add Njetiness for CHS
## 0064     process.load('RecoJets.JetProducers.nJettinessAdder_cfi')
## 0065     task.add(process.Njettiness)
## 0066     addToProcessAndTask('NjettinessAK8'+postfix, process.Njettiness.clone(), process, task)
## 0067     getattr(process,"NjettinessAK8").src = cms.InputTag("ak8PFJetsCHS"+postfix)
## 0068     getattr(process,"NjettinessAK8").cone = cms.double(0.8)
## 0069     getattr(process,"patJetsAK8").userData.userFloats.src += ['NjettinessAK8'+postfix+':tau1','NjettinessAK8'+postfix+':tau2','NjettinessAK8'+postfix+':tau3','NjettinessAK8'+postfix+':tau4']
## 0070 

    #----------------------------------------------------------------------------
    # add PF jet ID flags and jet energy corrections for AK12 pat::Jet collection,
    # following what is done for AK8 pat::Jets in https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/NanoAOD/python/jets_cff.py
    process.looseJetIdAK12 = process.looseJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetSubstructureSequence += process.looseJetIdAK12
    process.tightJetIdAK12 = process.tightJetIdAK8.clone(
        src = cms.InputTag(fatJetCollectionAK12)
    )
    process.jetSubstructureSequence += process.tightJetIdAK12
    process.jetsAK12WithUserData = process.slimmedJetsAK8WithUserData.clone(
        src = cms.InputTag(fatJetCollectionAK12),
        userInts = cms.PSet(
            looseId = cms.InputTag("looseJetIdAK12"),
            tightId = cms.InputTag("tightJetIdAK12")
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
        src = cms.InputTag('updatedJetsAK12'),
        jetRad = cms.double(1.2),
        jetAlgo = cms.string("AK")
    )
    process.jetSubstructureSequence += process.QJetsAdderAK12
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # add jet charge, pull, and Qjets volatility as userFloats to AK12 pat::Jet collection
    process.extendedFatJetsAK12 = cms.EDProducer("JetExtendedProducer",
        src = cms.InputTag('updatedJetsAK12'),
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
            subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int, doc="index of first subjet"),
            subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int, doc="index of second subjet"),
            subJetIdx3 = Var("?numberOfSourceCandidatePtrs()>2 && sourceCandidatePtr(2).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(2).key():-1", int, doc="index of third subjet"),
            tau1 = Var("userFloat('NjettinessAK12Puppi:tau1')",float, doc="Nsubjettiness (1 axis)",precision=10),
            tau2 = Var("userFloat('NjettinessAK12Puppi:tau2')",float, doc="Nsubjettiness (2 axis)",precision=10),
            tau3 = Var("userFloat('NjettinessAK12Puppi:tau3')",float, doc="Nsubjettiness (3 axis)",precision=10),
        )
    )
    process.jetSubstructureSequence += process.fatJetAK12Table
    process.subJetAK12Table = process.subJetTable.clone(
        src = cms.InputTag('extendedSubJetsAK12'),
        cut = cms.string(""),
        name = cms.string("SubJetAK12"),
        doc = cms.string("ak12 sub-jets for boosted analysis"),
        variables = cms.PSet(P4Vars)
    )
    process.jetSubstructureSequence += process.subJetAK12Table
    #----------------------------------------------------------------------------

    process.nanoSequence += process.jetSubstructureSequence

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
