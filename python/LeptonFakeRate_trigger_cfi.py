import FWCore.ParameterSet.Config as cms

leptonFR_triggers = {
  '2016' : {
    'mu' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Mu3_PFJet40"),
        cone_minPt = cms.double(10.),
        cone_maxPt = cms.double(32.),
        minRecoPt = cms.double(-1.),
        jet_minPt = cms.double(45.),
        average_prescale = cms.double(4849), # L=7.408/pb; present in all eras; prescale factor 4849.0 (4863.2 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu8"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(9123), # L=3.937/pb; present in all eras; prescale factor 9123.1 (9081.0 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu17"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(127.0), # L=282.781/pb; present in all eras; prescale factor 127.0 (127.4 from delivery)
        trigger_type = cms.string('2mu'),
      ),
    ),
    'e' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Ele8_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(45.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(5140), # L=6.988/pb; present in all eras; prescale factor 5140.3 (5135.5 from delivery)
        trigger_type = cms.string('2e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele17_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(25.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(572.4), # L=62.761/pb; present in all eras; prescale factor 572.4 (573.4 from delivery)
        trigger_type = cms.string('2e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele23_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(23.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(572.4), # L=62.7611/pb; present in all eras; prescale factor 572.4 (573.4 from delivery)
        trigger_type = cms.string('2e'),
      ),
    ),
  },
  '2017' : {
    'mu' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Mu3_PFJet40"),
        cone_minPt = cms.double(10.),
        cone_maxPt = cms.double(32.),
        minRecoPt = cms.double(-1.),
        jet_minPt = cms.double(45.),
        average_prescale = cms.double(9006), # L=4.611/pb; present in C, D, E, F, missing in B; prescale factor 9005.6 (8870.8 from delivery)
        trigger_type = cms.string('1mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu8"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(15943), # L=2.605/pb; present in all eras; prescale factor 15943.0 (15120.6 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu17"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(592.9), # L=70.038/pb; present in all eras; prescale factor 592.9 (600.1 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu20"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(20.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(72.3), # L=574.1/pb; present in all eras; prescale factor 72.3 (73.9 from delivery)
        trigger_type = cms.string('1mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu27"),
        cone_minPt = cms.double(45.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(27.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(224.5), # L=184.944/pb; present in all eras; prescale factor 224.5 (216.1 from delivery)
        trigger_type = cms.string('1mu'),
      ),
    ),
    'e' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Ele8_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(45.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(11364), # L=3.654/pb; present in C, D, E, F, missing in B; prescale factor 11363.9 (11029.2 from delivery)
        trigger_type = cms.string('1e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele17_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(25.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1167), # L=35.593/pb; present in C, D, E, F, missing in B; prescale factor 1166.8 (1181.3 from delivery)
        trigger_type = cms.string('1e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele23_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(23.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1087), # L=38.216/pb; present in C, D, E, F, missing in B; prescale factor 1086.7 (1101.5 from delivery)
        trigger_type = cms.string('1e'),
      ),
    ),
  },
  '2018' : {
    'mu' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Mu3_PFJet40"),
        cone_minPt = cms.double(10.),
        cone_maxPt = cms.double(32.),
        minRecoPt = cms.double(-1.),
        jet_minPt = cms.double(45.),
        average_prescale = cms.double(22160), # L=2.695/pb; present in all eras; prescale factor 22160.5 (22182.4 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu8"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(6990), # L=8.546/pb; present in all eras; prescale factor 6990.5 (6981.9 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu17"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1305), # L=45.781/pb; present in all eras; prescale factor 1304.9 (1307.1 from delivery)
        trigger_type = cms.string('2mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu20"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(20.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1081), # L=55.273/pb; present in all eras; prescale factor 1080.8 (1082.1 from delivery)
        trigger_type = cms.string('1mu'),
      ),
      cms.PSet(
        path = cms.string("HLT_Mu27"),
        cone_minPt = cms.double(45.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(27.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(475), # L=125.783/pb; present in all eras; prescale factor 475.0 (464.6 from delivery)
        trigger_type = cms.string('1mu'),
      ),
    ),
    'e' : cms.VPSet(
      cms.PSet(
        path = cms.string("HLT_Ele8_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(15.),
        cone_maxPt = cms.double(45.),
        minRecoPt = cms.double(8.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(9318), # L=6.411/pb; present in all eras; prescale factor 9318.5 (9325.6 from delivery)
        trigger_type = cms.string('1e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele17_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(25.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(17.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1537), # L=38.861/pb; present in all eras; prescale factor 1537.3 (1538.9 from delivery)
        trigger_type = cms.string('1e'),
      ),
      cms.PSet(
        path = cms.string("HLT_Ele23_CaloIdM_TrackIdM_PFJet30"),
        cone_minPt = cms.double(32.),
        cone_maxPt = cms.double(100.),
        minRecoPt = cms.double(23.),
        jet_minPt = cms.double(30.),
        average_prescale = cms.double(1537), # L=38.875/pb; present in all eras; prescale factor 1536.7 (1538.4 from delivery)
        trigger_type = cms.string('1e'),
      ),
    ),
  },
}

for era in leptonFR_triggers:
  for lepton in leptonFR_triggers[era]:
    for hlt_path in leptonFR_triggers[era][lepton]:
      if hlt_path.trigger_type.value() == '1mu':
        assert(lepton == 'mu')
        hlt_path.is_trigger_1mu = cms.bool(True)
        hlt_path.is_trigger_2mu = cms.bool(False)
        hlt_path.is_trigger_1e  = cms.bool(False)
        hlt_path.is_trigger_2e  = cms.bool(False)
      elif hlt_path.trigger_type.value() == '2mu':
        assert (lepton == 'mu')
        hlt_path.is_trigger_1mu = cms.bool(False)
        hlt_path.is_trigger_2mu = cms.bool(True)
        hlt_path.is_trigger_1e  = cms.bool(False)
        hlt_path.is_trigger_2e  = cms.bool(False)
      elif hlt_path.trigger_type.value() == '1e':
        assert (lepton == 'e')
        hlt_path.is_trigger_1mu = cms.bool(False)
        hlt_path.is_trigger_2mu = cms.bool(False)
        hlt_path.is_trigger_1e  = cms.bool(True)
        hlt_path.is_trigger_2e  = cms.bool(False)
      elif hlt_path.trigger_type.value() == '2e':
        assert (lepton == 'e')
        hlt_path.is_trigger_1mu = cms.bool(False)
        hlt_path.is_trigger_2mu = cms.bool(False)
        hlt_path.is_trigger_1e  = cms.bool(False)
        hlt_path.is_trigger_2e  = cms.bool(True)
      else:
        raise ValueError("Invalid trigger type: %s" % hlt_path.trigger_type.value())
