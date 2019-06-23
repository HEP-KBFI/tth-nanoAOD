from tthAnalysis.NanoAOD.LeptonFakeRate_trigger_cfi import leptonFR_triggers

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
        '1mu_noiso' : {
          'HLT_Mu45_eta2p1', # L=24.252/pb; present in all eras; prescaled in runs F, G, H
          'HLT_Mu50', # L=35.918/pb; present in all eras; unprescaled
          'HLT_TkMu50', # L=33.182/pb; present in all eras; unprescaled (enabled mid-run B)
        },
        '1e' : {
          'HLT_Ele27_WPTight_Gsf', # L=35.918/fb; present in all eras; unprescaled
          'HLT_Ele25_eta2p1_WPTight_Gsf', # L=35.918/fb; present in all eras; unprescaled
          'HLT_Ele27_eta2p1_WPLoose_Gsf', # L=27.303/fb; present in all eras; heavily prescaled in run H
        },
        '1e_noiso' : {
          'HLT_Ele105_CaloIdVT_GsfTrkIdT', # L=24.252/pb; present in all eras; prescaled in runs F, G, H
          'HLT_Ele115_CaloIdVT_GsfTrkIdT', # L=35.918/pb; present in all eras; unprescaled
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
        '1mu_noiso' : {
          'HLT_Mu50', # L=44.171/fb; present in all eras; unprescaled
          'HLT_Mu55', # L=27.121/fb; present in C, D, E, F; missing in B; slightly prescaled?
        },
        '1e' : {
          'HLT_Ele35_WPTight_Gsf', # L=41.527/fb; present in all eras; unprescaled
          'HLT_Ele32_WPTight_Gsf', # L=27.121/fb; present in D, E, F; missing in B, C; unprescaled
        },
        '1e_noiso' : {
          'HLT_Ele115_CaloIdVT_GsfTrkIdT', # L=36.733/fb; present in C, D, E, F; missing in B; unprescaled
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
        '1mu_noiso' : {
          'HLT_Mu50', # L=59.735/pb; present in all eras; unprescaled
          'HLT_OldMu100', # L=59.735/pb; present in all eras; unprescaled
          'HLT_TkMu100', # L=59.735/pb; present in all eras; unprescaled
        },
        '1e' : {
          'HLT_Ele32_WPTight_Gsf', # L=59.735/fb; present in all eras; unprescaled
          #'HLT_Ele35_WPTight_Gsf', # L=59.735; present in all eras; unprescaled (used by Alexei, but why ?)
        },
        '1e_noiso' : {
          'HLT_Ele115_CaloIdVT_GsfTrkIdT', # L=59.735/pb; present in all eras; unprescaled
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
      
    else:
      raise ValueError("Invalid era: %s" % era)
  
    self.triggers_leptonFR = {}
    for trigger_type in [ '1e', '1mu', '2e', '2mu' ]:
      self.triggers_leptonFR[trigger_type] = {
        hlt.path.value() for hlt in leptonFR_triggers[era][trigger_type[1:]] if hlt.trigger_type.value() == trigger_type
      }

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
