import FWCore.ParameterSet.Config as cms
from  PhysicsTools.NanoAOD.common_cff import *
from RecoJets.JetProducers.AnomalousCellParameters_cfi import *
from RecoJets.JetProducers.PFJetParameters_cfi import *
from RecoBTag.SecondaryVertex.pfCombinedInclusiveSecondaryVertexV2BJetTags_cfi import *
from RecoBTag.ImpactParameter.pfImpactParameterTagInfos_cfi import pfImpactParameterTagInfos
from RecoBTag.SecondaryVertex.pfInclusiveSecondaryVertexFinderTagInfos_cfi import *
from RecoBTag.SecondaryVertex.candidateCombinedSecondaryVertexV2Computer_cfi import *
from RecoBTag.SecondaryVertex.pfBoostedDoubleSVAK8TagInfos_cfi import *
from RecoBTag.Configuration.RecoBTag_cff import *
from Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff import *
from Configuration.Geometry.GeometryRecoDB_cff import *
from Configuration.Eras.Modifier_run2_miniAOD_80XLegacy_cff import run2_miniAOD_80XLegacy

##################### User floats producers, selectors ##########################

#Default parameters for HTTV2 and CA15 Fatjets
delta_r = 1.5
jetAlgo = "CambridgeAachen"
subjet_label = "SubJets"
initial_jet = "ca15PFJetsCHS"
maxSVDeltaRToJet = 1.3
weightFile = 'RecoBTag/SecondaryVertex/data/BoostedDoubleSV_CA15_BDT_v3.weights.xml.gz'

######################
####    HTTV2     ####
######################

# Get input objects for HTTV2 calculation
selectedMuonsTmp = cms.EDProducer("MuonRemovalForBoostProducer", 
    src = cms.InputTag("slimmedMuons"),
    vtx = cms.InputTag("offlineSlimmedPrimaryVertices"))
selectedMuons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedMuonsTmp"), 
    cut = cms.string("1"))
selectedElectronsTmp = cms.EDProducer("ElectronRemovalForBoostProducer", 
    src = cms.InputTag("slimmedElectrons"),
    mvaIDMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight"),
    rho = cms.InputTag("fixedGridRhoFastjetAll"))
run2_miniAOD_80XLegacy.toModify(
    selectedElectronsTmp,
    mvaIDMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight")
)
selectedElectrons = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("selectedElectronsTmp"), 
    cut = cms.string("1"))
chsTmp1 = cms.EDFilter("CandPtrSelector", 
    src = cms.InputTag("packedPFCandidates"), 
    cut = cms.string("fromPV")) 
chsTmp2 =  cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp1"), 
    veto = cms.InputTag("selectedMuons"))
chs = cms.EDProducer("CandPtrProjector", 
    src = cms.InputTag("chsTmp2"), 
    veto = cms.InputTag("selectedElectrons")) 

#Calculate HTT tagger
looseOptRHTT = cms.EDProducer(
            "HTTTopJetProducer",
            PFJetParameters.clone(
                src               = cms.InputTag("chs"),
                doAreaFastjet     = cms.bool(True),
                doRhoFastjet      = cms.bool(False),
                jetPtMin          = cms.double(200.0)
                ),
            AnomalousCellParameters,
            useExplicitGhosts = cms.bool(True),
            algorithm           = cms.int32(1),
            jetAlgorithm        = cms.string("CambridgeAachen"),
            rParam              = cms.double(1.5),
            optimalR            = cms.bool(True),
            qJets               = cms.bool(False),
            minFatjetPt         = cms.double(200.),
            minSubjetPt         = cms.double(0.),
            minCandPt           = cms.double(0.),
            maxFatjetAbsEta     = cms.double(99.),
            subjetMass          = cms.double(30.),
            muCut               = cms.double(0.8),
            filtR               = cms.double(0.3),
            filtN               = cms.int32(5),
            mode                = cms.int32(4),
            minCandMass         = cms.double(0.),
            maxCandMass         = cms.double(999999.),
            massRatioWidth      = cms.double(999999.),
            minM23Cut           = cms.double(0.),
            minM13Cut           = cms.double(0.),
            maxM13Cut           = cms.double(999999.),
            writeCompound       = cms.bool(True),
            jetCollInstanceName = cms.string("SubJets")
            )

#Calculate subjet btags
looseOptRHTTImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("chs"),
    computeGhostTrack = cms.bool(True),
    computeProbabilities = cms.bool(True),
    maxDeltaR = cms.double(0.4),
    jets = cms.InputTag("looseOptRHTT", "SubJets")
)

looseOptRHTTImpactParameterTagInfos.explicitJTA = cms.bool(True)

looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("looseOptRHTTImpactParameterTagInfos"),                
)

looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(True)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(0.3)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(0.3)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(0.4)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.fatJets  =  cms.InputTag(initial_jet)
looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos.groomedFatJets = cms.InputTag("looseOptRHTT","")

looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags = pfCombinedInclusiveSecondaryVertexV2BJetTags.clone(
    tagInfos = cms.VInputTag(cms.InputTag("looseOptRHTTImpactParameterTagInfos"),
                             cms.InputTag("looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos")),
    jetTagComputer = cms.string("candidateCombinedSecondaryVertexV2Computer")
)

looseOptRHTTpatSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                       
    embedGenPartonMatch = cms.bool(False), 
    genPartonMatch      = cms.InputTag(""),     
    addGenJetMatch      = cms.bool(False),                       
    embedGenJetMatch    = cms.bool(False),                       
    genJetMatch         = cms.InputTag(""),     
    addPartonJetMatch   = cms.bool(False),
    partonJetSource     = cms.InputTag(""),       
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag(""),
    JetFlavourInfoSource = cms.InputTag(""),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

#This reorders the subjets as in the original subjet list (ordered by pt in the patjet conversion)
looseOptRHTTSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("looseOptRHTT", "SubJets"),
    patsubjets = cms.InputTag("looseOptRHTTpatSubJets")
)

#Now, make all the tables
HTTV2Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("looseOptRHTT"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("HTTV2"),
    doc  = cms.string("HTTV2 candidates calculated from CA15 fatjets"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars,
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int,
             doc="index of first subjet"),
        subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int,
             doc="index of second subjet"),
        subJetIdx3 = Var("?numberOfSourceCandidatePtrs()>2 && sourceCandidatePtr(2).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(2).key():-1", int,
             doc="index of third subjet"),    
    )
)

#Get HTTV2 variables:  fRec,Ropt...
HTTV2InfoTable = cms.EDProducer("SimpleHTTInfoFlatTableProducer",
    src = cms.InputTag("looseOptRHTT"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("HTTV2"),
    doc  = cms.string("Information to HTT candidates"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(True), 
    variables = cms.PSet(
        fRec = Var("abs(properties().fRec())", float, doc="relative W width",precision=10),
        Ropt = Var("properties().ropt()", float, doc="optimal value of R",precision=10),
        RoptCalc = Var("properties().roptCalc()", float, doc="expected value of optimal R",precision=10),
        ptForRoptCalc = Var("properties().ptForRoptCalc()", float, doc="pT used for calculation of RoptCalc",precision=10)
    )
)

#Add HTT subjets
HTTV2SubjetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("looseOptRHTTSubjetsOrdered"),
    cut = cms.string(""),
    name = cms.string("HTTV2Subjets"),
    doc  = cms.string("Btags of HTT candidate subjets"),
    singleton = cms.bool(False),
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars,
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.99 || neutralEmEnergyFraction() >= 0.99 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0 || chargedEmEnergyFraction() >= 0.99?0:1",float, doc="Subjet ID passed?",precision=1),
        btag  = Var("bDiscriminator('looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc="CSV V2 btag discriminator",precision=10),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
    )
)



#############################
####    CA15 Fatjets     ####
#############################

ca15PFJetsCHS = cms.EDProducer(
    "FastjetJetProducer",
    PFJetParameters,
    AnomalousCellParameters,
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(1.5))
    
ca15PFJetsCHS.src = cms.InputTag("chs")
ca15PFJetsCHS.jetPtMin = cms.double(200.)

#Hbb tag
ca15PFJetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("packedPFCandidates"),
    computeProbabilities = cms.bool(False),
    computeGhostTrack = cms.bool(False),
    maxDeltaR = cms.double(delta_r),
    jets = cms.InputTag("ca15PFJetsCHS"),
)

ca15PFJetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(False)

ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFJetsCHSImpactParameterTagInfos"),                
)

ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(False)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(delta_r)
ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)

ca15PFJetsCHSpfBoostedDoubleSVTagInfos = pfBoostedDoubleSVAK8TagInfos.clone(
    svTagInfos = cms.InputTag("ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos"),
)

ca15PFJetsCHSpfBoostedDoubleSVTagInfos.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer = cms.ESProducer("CandidateBoostedDoubleSecondaryVertexESProducer",
   trackSelectionBlock,
   beta = cms.double(1.0),
   R0 = cms.double(delta_r),
   maxSVDeltaRToJet = cms.double(maxSVDeltaRToJet),
   useCondDB = cms.bool(False),
   weightFile = cms.FileInPath(weightFile),
   useGBRForest = cms.bool(True),
   useAdaBoost = cms.bool(False),
   trackPairV0Filter = cms.PSet(k0sMassWindow = cms.double(0.03))
)

ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer.trackSelection.jetDeltaRMax = cms.double(delta_r)

ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags = cms.EDProducer("JetTagProducer",
    jetTagComputer = cms.string("ca15PFJetsCHScandidateBoostedDoubleSecondaryVertexComputer"),
    tagInfos = cms.VInputTag(cms.InputTag("ca15PFJetsCHSpfBoostedDoubleSVTagInfos"))
)

ca15PFJetsCHSpatFatjet = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFJetsCHS"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                          ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                          ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag(""),                         ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                          ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                          ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag(""),                         ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag(""),                         ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag(""),
    JetFlavourInfoSource = cms.InputTag(""),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFJetsCHSFatjetOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFJetsCHS"),
    patsubjets = cms.InputTag("ca15PFJetsCHSpatFatjet")
)

ca15PFJetsCHSNSubjettiness  = cms.EDProducer("NjettinessAdder",
    src=cms.InputTag("ca15PFJetsCHSFatjetOrdered"),
    cone=cms.double(1.5),
    Njets = cms.vuint32(1,2,3),
    # variables for measure definition : 
    measureDefinition = cms.uint32( 0 ), # CMS default is normalized measure
    beta = cms.double(1.0),              # CMS default is 1
    R0 = cms.double(1.5),                # CMS default is jet cone size
    Rcutoff = cms.double( 999.0),       # not used by default
    # variables for axes definition :
    axesDefinition = cms.uint32( 6 ),    # CMS default is 1-pass KT axes
    nPass = cms.int32(999),             # not used by default
    akAxesR0 = cms.double(-999.0)        # not used by default
)

FatjetsWithUserData = cms.EDProducer("PATJetUserDataEmbedder",
     src = cms.InputTag("ca15PFJetsCHSFatjetOrdered"),
     userFloats = cms.PSet(
        tau1= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau1"),
        tau2= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau2"),
        tau3= cms.InputTag("ca15PFJetsCHSNSubjettiness:tau3"),
     ),
)

finalFatjets = cms.EDFilter("PATJetRefSelector",
    src = cms.InputTag("FatjetsWithUserData"),
    cut = cms.string("pt > 5 ")
)

#Make all tables 
ca15Table = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFJetsCHS"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15"),
    doc  = cms.string("CA15 fatjets (ungroomed)"), 
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
    )
)

#Add Nsubjettiness and BBtag
FatjetBBTagTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("finalFatjets"),
    cut = cms.string(""),
    name = cms.string("FatjetCA15"),
    doc  = cms.string("CA15 fatjets (ungroomed)"),    
    singleton = cms.bool(False),
    extension = cms.bool(True), 
    variables = cms.PSet(
        bbtag  = Var("bDiscriminator('ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags')",float,doc="Double btag discriminator",precision=10),
        tau1  = Var("userFloat('tau1')",float,doc="N-subjettiness",precision=10),
        tau2  = Var("userFloat('tau2')",float,doc="N-subjettiness",precision=10),
        tau3  = Var("userFloat('tau3')",float,doc="N-subjettiness",precision=10),
    )
)


######################################
####    CA15 Softdrop Fatjets     ####
######################################

# Apply softdrop to CA R=1.5 jets
ca15PFSoftdropJetsCHS = ca15PFJetsCHS.clone(
    useSoftDrop = cms.bool(True),
    zcut = cms.double(0.1),
    beta = cms.double(0.0),
    R0 = cms.double(1.5),
    useExplicitGhosts = cms.bool(True), 
    writeCompound = cms.bool(True), # Also write subjets
    jetCollInstanceName=cms.string("SubJets"),            
)

#Get Softdrop subjet btags
ca15PFSoftdropJetsCHSImpactParameterTagInfos = pfImpactParameterTagInfos.clone(
    primaryVertex = cms.InputTag("offlineSlimmedPrimaryVertices"),
    candidates = cms.InputTag("chs"),
    computeGhostTrack = cms.bool(True),
    computeProbabilities = cms.bool(True),
    maxDeltaR = cms.double(0.4),
    jets = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets")
)

ca15PFSoftdropJetsCHSImpactParameterTagInfos.explicitJTA = cms.bool(True)

ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos = pfInclusiveSecondaryVertexFinderTagInfos.clone(
    extSVCollection = cms.InputTag('slimmedSecondaryVertices'),
    trackIPTagInfos = cms.InputTag("ca15PFSoftdropJetsCHSImpactParameterTagInfos"),                
)

ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.useSVClustering = cms.bool(True)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.rParam = cms.double(delta_r)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.extSVDeltaRToJet = cms.double(0.3)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.trackSelection.jetDeltaRMax = cms.double(0.3)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.vertexCuts.maxDeltaRToJetAxis = cms.double(0.4)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.jetAlgorithm = cms.string(jetAlgo)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.fatJets  =  cms.InputTag(initial_jet)
ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos.groomedFatJets = cms.InputTag("ca15PFSoftdropJetsCHS","")


ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags = pfCombinedInclusiveSecondaryVertexV2BJetTags.clone(
    tagInfos = cms.VInputTag(cms.InputTag("ca15PFSoftdropJetsCHSImpactParameterTagInfos"),
                             cms.InputTag("ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos")),
    jetTagComputer = cms.string("candidateCombinedSecondaryVertexV2Computer")
)

ca15PFSoftdropJetsCHSpatSubJets = cms.EDProducer("PATJetProducer",
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets"),
    embedPFCandidates = cms.bool(False),
    addJetCorrFactors    = cms.bool(False),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetCorrFactors") ),
    # btag information
    addBTagInfo          = cms.bool(True),   ## master switch
    addDiscriminators    = cms.bool(True),   ## addition btag discriminators
    discriminatorSources = cms.VInputTag(
        cms.InputTag("ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags"),
    ),
    addTagInfos     = cms.bool(False),
    tagInfoSources  = cms.VInputTag(),
    addAssociatedTracks    = cms.bool(False),
    trackAssociationSource = cms.InputTag("ak4JetTracksAssociatorAtVertexPF"),
    addJetCharge    = cms.bool(False),
    jetChargeSource = cms.InputTag("patJetCharge"),
    addJetID = cms.bool(False),
    jetIDMap = cms.InputTag("ak4JetID"),
    addGenPartonMatch   = cms.bool(False),                          ## switch on/off matching to quarks from hard scatterin
    embedGenPartonMatch = cms.bool(False),                          ## switch on/off embedding of the GenParticle parton for this jet
    genPartonMatch      = cms.InputTag(""),                         ## particles source to be used for the matching
    addGenJetMatch      = cms.bool(False),                          ## switch on/off matching to GenJet's
    embedGenJetMatch    = cms.bool(False),                          ## switch on/off embedding of matched genJet's
    genJetMatch         = cms.InputTag(""),                         ## GenJet source to be used for the matching
    addPartonJetMatch   = cms.bool(False),                          ## switch on/off matching to PartonJet's (not implemented yet)
    partonJetSource     = cms.InputTag(""),                         ## ParticleJet source to be used for the matching
    getJetMCFlavour    = cms.bool(False),
    useLegacyJetMCFlavour = cms.bool(False),
    addJetFlavourInfo  = cms.bool(False),
    JetPartonMapSource = cms.InputTag(""),
    JetFlavourInfoSource = cms.InputTag(""),
    addEfficiencies = cms.bool(False),
    efficiencies    = cms.PSet(),
    addResolutions = cms.bool(False),
    resolutions     = cms.PSet()
)

ca15PFSoftdropJetsCHSSubjetsOrdered =  cms.EDProducer("HTTBtagMatchProducer", 
    jetSource = cms.InputTag("ca15PFSoftdropJetsCHS", "SubJets"),
    patsubjets = cms.InputTag("ca15PFSoftdropJetsCHSpatSubJets")
)

#Make all tables
ca15SoftDropTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdropJetsCHS"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDrop"),
    doc  = cms.string("Softdrop CA15 fatjets (zcut = 0.1, beta = 0)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        subJetIdx1 = Var("?numberOfSourceCandidatePtrs()>0 && sourceCandidatePtr(0).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(0).key():-1", int,
             doc="index of first subjet"),
        subJetIdx2 = Var("?numberOfSourceCandidatePtrs()>1 && sourceCandidatePtr(1).numberOfSourceCandidatePtrs()>0?sourceCandidatePtr(1).key():-1", int,
             doc="index of second subjet"),    
    )
)

ca15SoftDropSubjetsTable = cms.EDProducer("SimpleCandidateFlatTableProducer",
    src = cms.InputTag("ca15PFSoftdropJetsCHSSubjetsOrdered"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("FatjetCA15SoftDropSubjets"),
    doc  = cms.string("Softdrop CA15 subjets (zcut = 0.1, beta = 0)"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), 
    variables = cms.PSet(P4Vars, 
        #jetId = Var("userInt('tightId')*2+userInt('looseId')",int,doc="Jet ID flags bit1 is loose, bit2 is tight"),
        area = Var("jetArea()", float, doc="jet catchment area, for JECs",precision=10),
        btag  = Var("bDiscriminator('ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags')",float,doc="CMVA V2 btag discriminator",precision=10),
        IDPassed = Var("?pt() <= 20 || abs(eta()) >= 2.4 || neutralHadronEnergyFraction()>=0.99 || neutralEmEnergyFraction() >= 0.99 ||(chargedMultiplicity()+neutralMultiplicity()) <= 1 || chargedHadronEnergyFraction() <= 0 || chargedMultiplicity() <= 0 || chargedEmEnergyFraction() >= 0.99?0:1",float, doc="Subjet ID passed?",precision=1),
    )
)

boostedSequence = cms.Sequence(
    #Prepare input objects
    selectedMuonsTmp+selectedMuons+selectedElectronsTmp+selectedElectrons+chsTmp1+chsTmp2+chs+ca15PFJetsCHS+ \
    #HTTV2 + subjet btags
    looseOptRHTT+looseOptRHTTImpactParameterTagInfos+looseOptRHTTpfInclusiveSecondaryVertexFinderTagInfos+ \
    looseOptRHTTpfCombinedInclusiveSecondaryVertexV2BJetTags+looseOptRHTTpatSubJets+looseOptRHTTSubjetsOrdered+ \
    #CA15 double btag
    ca15PFJetsCHSImpactParameterTagInfos+ca15PFJetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFJetsCHSpfBoostedDoubleSVTagInfos+ca15PFJetsCHSpfBoostedDoubleSecondaryVertexBJetTags+ \
    ca15PFJetsCHSpatFatjet+ca15PFJetsCHSFatjetOrdered+ca15PFJetsCHSNSubjettiness+FatjetsWithUserData+finalFatjets+ \
    #Softdrop CA15 jets + subjet btags
    ca15PFSoftdropJetsCHS+ca15PFSoftdropJetsCHSImpactParameterTagInfos+ ca15PFSoftdropJetsCHSpfInclusiveSecondaryVertexFinderTagInfos+ \
    ca15PFSoftdropJetsCHSpfCombinedInclusiveSecondaryVertexV2BJetTags+ \
    ca15PFSoftdropJetsCHSpatSubJets+ca15PFSoftdropJetsCHSSubjetsOrdered
)
boostedTables = cms.Sequence(HTTV2Table+HTTV2InfoTable+HTTV2SubjetsTable+ \
    ca15Table+FatjetBBTagTable+ca15SoftDropTable+ca15SoftDropSubjetsTable)

