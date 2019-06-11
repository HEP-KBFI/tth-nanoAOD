
class Triggers(object):

  def __init__(self, era):

    if era == "2016":
      self.triggers_analysis = {
        '3mu' : {
          'HLT_TripleMu_12_10_5', # L=35.918/fb; present in all eras; unprescaled
        },
        '1e2mu' : {
          'HLT_DiMu9_Ele9_CaloIdL_TrackIdL', # L=35.918/fb; present in all eras; unprescaled
        },
        '2e1mu' : {
          'HLT_Mu8_DiEle12_CaloIdL_TrackIdL', # L=35.918/fb; present in all eras; unprescaled
        },
        '3e' : {
          'HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL', # L=35.918/fb; present in all eras; unprescaled
        },
        '2mu' : {
          'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL', # L=27.655/fb; present in all eras, prescaled in run H
          'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', # L=35.918/fb; present in all eras; unprescaled
          'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL', # L=27.655/fb; present in all eras, prescaled in run H
          'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ', # L=35.918/fb; present in all eras; unprescaled
        },
        '1e1mu' : {
          'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL', # L=27.267/fb; present in B, C, D, E, F, G, missing in H; unprescaled
          'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', # L=18.277/fb; present in F, G, H; unprescaled
          'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', # L=27.267/fb; present in B, C, D, E, F, G, missing in H
          'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ', # L=8650/pb; present in H, missing in B, C, D, E, F, G; unprescaled
          
        },
        '2e' : {
          'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', # L=35.918/fb; present in all eras; unprescaled
        },
        '1mu' : {
          'HLT_IsoMu22', # L=28.564/fb; present in all eras; prescaled since mid run E til the end of 2016
          'HLT_IsoTkMu22', # L=28.564/fb; present in all eras; prescaled since mid run E til the end of 2016
          'HLT_IsoMu22_eta2p1', # L=33.182/fb; present in all eras (introduced mid B); unprescaled
          'HLT_IsoTkMu22_eta2p1', # L=33.182/fb; present in all eras (introduced mid B); unprescaled
          'HLT_IsoMu24', # L=35.918/fb; present in all eras; unprescaled
          'HLT_IsoTkMu24', # L=35.918/fb; present in all eras; unprescaled
        },
        '1e' : {
          'HLT_Ele27_WPTight_Gsf', # L=35.918/fb; present in all eras; unprescaled
          'HLT_Ele25_eta2p1_WPTight_Gsf', # L=35.918/fb; present in all eras; unprescaled
          'HLT_Ele27_eta2p1_WPLoose_Gsf', # L=27.303/fb; present in all eras; heavily prescaled in run H
        },
        '1mu1tau' : {
          'HLT_IsoMu19_eta2p1_LooseIsoPFTau20_SingleL1', # L=35.918/fb; present in all eras; unprescaled
        },
        '1e1tau' : {
          'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', # L=17.144/fb; present in B, C, D, E, F, missing in G, H; unprescaled (effectively prescaled by 2.1)
          'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20_SingleL1', # L=17.640/fb; present in B, C, D, E, F, missing in G, H; unprescaled (effectively prescaled by 2.0)
          'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau30', # L=22.883/fb; present in E, F, G, H; missing in B, C, D; unprescaled
        },
        '2tau' : {
          'HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg', # L=27.267/fb; present in B, C, D, E, F, G, missing in H; unprescaled
          'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg', # L=8650.63/pb; present in H, missing in B, C, D, E, F, G; unprescaled (effectively presscaled by 4.2)
        },
      }

      self.triggers_leptonFR = {
        '1e' : set(),
        '1mu': {
          'HLT_Mu27', # L=250.508/pb; present in all eras; prescale factor 143.4 (143.0 from delivery)
        },
        '2e' : {
          'HLT_Ele17_CaloIdM_TrackIdM_PFJet30', # L=62.761/pb; present in all eras; prescale factor 572.4 (573.4 from delivery)
          'HLT_Ele12_CaloIdM_TrackIdM_PFJet30', # L=17.714/pb; present in all eras; prescale factor 2027.9 (2032.1 from delivery)
        },
        '2mu': {
          'HLT_Mu17', # L=282.781/pb; present in all eras; prescale factor 127.0 (127.4 from delivery)
          'HLT_Mu8', # L=3.937/pb; present in all eras; prescale factor 9123.1 (9081.0 from delivery)
          'HLT_Mu3_PFJet40', # L=7.408/pb; present in all eras; prescale factor 4849.0 (4863.2 from delivery)
        }
      }
    elif era == "2017":
      self.triggers_analysis = {
        '3mu' : {
          'HLT_TripleMu_12_10_5', # L=41.527/fb; present in all eras; unprescaled
        },
        '1e2mu' : {
          'HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ', # L=41.527/fb; present in all eras; unprescaled
        },
        '2e1mu' : {
          'HLT_Mu8_DiEle12_CaloIdL_TrackIdL', # L=41.527/fb; present in all eras; unprescaled (+ DZ IS DOCUMENTED ON GITLAB)
        },
        '3e' : {
          'HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL', # L=35.997/fb; present in all eras; unprescaled (has PU dependence)
        },
        '2mu' : {
          'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8', # L=36.733/fb; present in C, D, E, F, missing in B; unprescaled
          'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8', # L=41.527/fb; present in all eras; unprescaled
        },
        '1e1mu' : {
          'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', # L=41.527/fb; present in all eras; unprescaled
          'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', # L=41.527/fb; present in all eras; unprescaled
          'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL', # L=36.733/fb; present in C, D, E, F, missing in B; unprescaled
          'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', # L=41.527/fb; present in all eras; unprescaled
        },
        '2e' : {
          'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL', # L=41.527/fb; present in all eras; unprescaled (higher efficiency than non-DZ; not present in B)
        },
        '1mu' : {
          'HLT_IsoMu24', # L=38.046/fb; present in all eras; unprescaled (not enabled at high lumi)
          'HLT_IsoMu27', # L=41.527/fb; present in all eras; unprescaled
        },
        '1e' : {
          'HLT_Ele35_WPTight_Gsf', # L=41.527/fb; present in all eras; unprescaled
          'HLT_Ele32_WPTight_Gsf', # L=27.121/fb; present in D, E, F; missing in B, C; unprescaled
        },
        # CV: tau trigger paths taken from slide 6 of presentation given by Hale Sert at HTT workshop in December 2017
        #    (https://indico.cern.ch/event/684622/contributions/2807071/attachments/1575421/2487940/141217_triggerStatusPlans_hsert.pdf),
        #     except that the 'HLT_IsoMu24_eta2p1_LooseChargedIsoPFTau20_SingleL1' path has been dropped,
        #     as it was found to increase the trigger acceptance only marginally
        #    (cf. slide 19 of https://indico.cern.ch/event/683144/contributions/2814995/attachments/1570846/2478034/Ruggles_TauTriggers_TauPOG_20171206_v7.pdf)
        '1mu1tau' : { # stored in SingleMuon dataset
          'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', # L=41.527/fb; present in all eras; unprescaled
        },
        '1e1tau' : { # stored in SingleElectron dataset
          'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', # L=41.527/fb; present in all eras; unprescaled
        },
        '2tau' : { # stored in Tau dataset
          'HLT_DoubleMediumChargedIsoPFTau35_Trk1_eta2p1_Reg', # L=36.003/fb; present in all eras; unprescaled
          'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', # L=41.527/fb; present in all eras; unprescaled
          'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', # L=41.527/fb; present in all eras; unprescaled
          'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', # L=41.527/fb; present in all eras; unprescaled
        },
      }

      self.triggers_leptonFR = {
        '1e' : {
          'HLT_Ele8_CaloIdM_TrackIdM_PFJet30', # L=3.654/pb; present in C, D, E, F, missing in B; prescale factor 11363.9 (11029.2 from delivery)
          'HLT_Ele17_CaloIdM_TrackIdM_PFJet30', # L=35.593/pb; present in C, D, E, F, missing in B; prescale factor 1166.8 (1181.3 from delivery)
          'HLT_Ele23_CaloIdM_TrackIdM_PFJet30', # L=38.216/pb; present in C, D, E, F, missing in B; prescale factor 1086.7 (1101.5 from delivery)
        },
        '1mu' : {
          'HLT_Mu27', # L=184.944/pb; present in all eras; prescale factor 224.5 (216.1 from delivery)
          'HLT_Mu20', # L=574.1/pb; present in all eras; prescale factor 72.3 (73.9 from delivery)
          'HLT_Mu3_PFJet40', # L=4.611/pb; present in C, D, E, F, missing in B; prescale factor 9005.6 (8870.8 from delivery)
        },
        '2e' : set(),
        '2mu' : {
          'HLT_Mu17', # L=70.038/pb; present in all eras; prescale factor 592.9 (600.1 from delivery)
          'HLT_Mu8', # L=2.605/pb; present in all eras; prescale factor 15943.0 (15120.6 from delivery)
        }
      }
    elif era == "2018":
      self.triggers_analysis = {
        '3mu' : {
          'HLT_TripleMu_12_10_5', # L=59.735/fb; present in all eras; unprescaled
        },
        '1e2mu' : {
          'HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ', # L=59.735/fb; present in all eras; unprescaled
        },
        '2e1mu' : {
          'HLT_Mu8_DiEle12_CaloIdL_TrackIdL', # L=59.735/fb; present in all eras; unprescaled
        },
        '3e' : {
          'HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL', # L=54.444/fb; present in all eras; unprescaled
        },
        '2mu' : {
          'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8', # L=59.735/fb; present in all eras; unprescaled
        },
        '1e1mu' : {
          'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', # L=59.735/fb; present in all eras; unprescaled
          'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', # L=59.735/fb; present in all eras; unprescaled
          'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL', # L=59.735/fb; present in all eras; unprescaled
        },
        '2e' : {
          'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL', # L=59.735/fb; present in all eras; unprescaled
          #'HLT_DoubleEle25_CaloIdL_MW', # L=59.735/fb; present in all eras; unprescaled (used by H->ZZ->4 lepton analysis, but why ?)
        },
        '1mu' : {
          'HLT_IsoMu24', # L=59.727/fb; present in all eras; unprescaled
          'HLT_IsoMu27', # L=59.735/fb; present in all eras; unprescaled
        },
        '1e' : {
          'HLT_Ele32_WPTight_Gsf', # L=59.735/fb; present in all eras; unprescaled
          #'HLT_Ele35_WPTight_Gsf', # L=59.735; present in all eras; unprescaled (used by Alexei, but why ?)
        },
        # CV: tau trigger paths taken from slide 12 of presentation given by Hale Sert at HTT workshop in April 2019
        #    (https://indico.cern.ch/event/803335/contributions/3359970/attachments/1829789/2996369/TriggerStatus_HTTworkshop_hsert.pdf)
        '1mu1tau' : { # stored in SingleMuon dataset
          'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTau27_eta2p1_CrossL1', # L=17.682/fb; present in eras A, B, missing in C, D; unprescaled (effectively prescaled by 3.4); not in MC
          'HLT_IsoMu20_eta2p1_LooseChargedIsoPFTauHPS27_eta2p1_CrossL1', # L=59.735/fb; present in all eras; unprescaled; not in MC
        },
        '1e1tau' : { # stored in SingleElectron dataset?
          'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTau30_eta2p1_CrossL1', # L=17.682/fb; present in eras A, B, missing in C, D; unprescaled (effectively prescaled by 3.4); not in MC
          'HLT_Ele24_eta2p1_WPTight_Gsf_LooseChargedIsoPFTauHPS30_eta2p1_CrossL1', # L=42.053/fb; present in eras B, C, D, missing in A; unprescaled
        },
        '2tau' : { # stored in Tau dataset
          'HLT_DoubleTightChargedIsoPFTau35_Trk1_TightID_eta2p1_Reg', # L=17.682/fb; present in eras A, B, missing in C, D; unprescaled (effectively prescaled by 3.4); not in MC
          'HLT_DoubleMediumChargedIsoPFTau40_Trk1_TightID_eta2p1_Reg', # L=17.682/fb; present in eras A, B, missing in C, D; unprescaled (effectively prescaled by 3.4); not in MC
          'HLT_DoubleTightChargedIsoPFTau40_Trk1_eta2p1_Reg', # L=17.682/fb; present in eras A, B, missing in C, D; unprescaled (effectively prescaled by 3.4); not in MC
          'HLT_DoubleMediumChargedIsoPFTauHPS35_Trk1_eta2p1_Reg', # L=59.735/fb; present in all eras; unprescaled
        },
      }

      self.triggers_leptonFR = {
        '1e' : {
          'HLT_Ele8_CaloIdM_TrackIdM_PFJet30', # L=6.411/pb; present in all eras; prescale factor 9318.5 (9325.6 from delivery)
          'HLT_Ele17_CaloIdM_TrackIdM_PFJet30', # L=38.861/pb; present in all eras; prescale factor 1537.3 (1538.9 from delivery)
          'HLT_Ele23_CaloIdM_TrackIdM_PFJet30', # L=38.875/pb; present in all eras; prescale factor 1536.7 (1538.4 from delivery)
        },
        '1mu' : {
          'HLT_Mu27', # L=125.783/pb; present in all eras; prescale factor 475.0 (464.6 from delivery)
          'HLT_Mu20', # L=55.273/pb; present in all eras; prescale factor 1080.8 (1082.1 from delivery)
          'HLT_Mu3_PFJet40', # L=2.695/pb; present in all eras; prescale factor 22160.5 (22182.4 from delivery)
        },
        '2e' : set(),
        '2mu' : {
          'HLT_Mu17', # L=45.781/pb; present in all eras; prescale factor 1304.9 (1307.1 from delivery)
          'HLT_Mu8', # L=8.546/pb; present in all eras; prescale factor 6990.5 (6981.9 from delivery)
        }
      }
    else:
      raise ValueError("Invalid era: %s" % era)

    self.triggers_all = {}
    for trigger_name in list(set(self.triggers_analysis.keys()) | set(self.triggers_leptonFR.keys())):
      self.triggers_all[trigger_name] = set()
      if trigger_name in self.triggers_analysis:
        self.triggers_all[trigger_name].update(self.triggers_analysis[trigger_name])
      if trigger_name in self.triggers_leptonFR:
        self.triggers_all[trigger_name].update(self.triggers_leptonFR[trigger_name])

    self.triggers_analysis_flat = { trigger for triggers in self.triggers_analysis for trigger in self.triggers_analysis[triggers] }
    self.triggers_leptonFR_flat = { trigger for triggers in self.triggers_leptonFR for trigger in self.triggers_leptonFR[triggers] }
    self.triggers_flat          = self.triggers_analysis_flat | self.triggers_leptonFR_flat
