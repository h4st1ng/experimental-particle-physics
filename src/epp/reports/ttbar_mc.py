# Configuración global de anàlisis de ttbar

# Librerías
import ROOT
import numpy as np

#--- Global parameters ---#

DATASET_NAME = 'ttbar_8TeV.root'
TREE_NAME = "mini"


#--- Raw features ---#

RAW_FEATURES = {
    "mcWeight":{"name":"mcWeight", "ptype":"scalar"}, # Event weight
    "trigE":{"name":"trig_e", "ptype":"scalar"}, # Triger electromagnético
    "trigM":{"name":"trig_m", "ptype":"scalar"}, # Triger muonico
    "hasGoodVertex":{"name":"good_vertex", "ptype":"scalar"}, # Vértice válido    
    "lep_n":{"name":"lep_n", "ptype":"scalar"}, # Número de leptones
    "lep_pt":{"name":"lep_pt", "ptype":"vector"}, # PT de los leptones
    "lep_eta":{"name":"lep_eta", "ptype":"vector"}, # Dirección polar de los leptones
    "lep_phi":{"name":"lep_phi", "ptype":"vector"}, # Direccion azimutual de los leptones
    "lep_E":{"name":"lep_E", "ptype":"vector"}, # Energía de los leptones
    "lep_type":{"name":"lep_type", "ptype":"vector"}, # Tipo de lepton
    "lep_ptcone30":{"name":"lep_ptcone30", "ptype":"vector"}, # Track isolation lepton
    "lep_etcone20":{"name":"lep_etcone20", "ptype":"vector"},# Calorimeter isolation lepton
    "jet_n":{"name":"jet_n", "ptype":"scalar"}, # Numero de jets
    "jet_pt":{"name":"jet_pt", "ptype":"vector"}, # PT de los Jets
    "jet_eta":{"name":"jet_eta", "ptype":"vector"}, # Eta jets
    "jet_jvf":{"name":"jet_jvf", "ptype":"vector"}, # JVF jets
    "jet_MV1":{"name":"jet_mv1", "ptype":"vector"},# MV1 jets 
    "met_et":{"name":"met_et", "ptype":"scalar"}, # Energía transversa faltanate
    "met_phi":{"name":"met_phi", "ptype":"scalar"},# Angulo azimutal de la MET.
    "scaleFactor_PILEUP":{"name":"scaleFactor_PILEUP", "ptype":"scalar"}, # scaleFactor_PILEUP
    "scaleFactor_ELE":{"name":"scaleFactor_ELE", "ptype":"scalar"}, # scaleFactor_ELE
    "scaleFactor_MUON":{"name":"scaleFactor_MUON", "ptype":"scalar"}, # scaleFactor_MUON
    "scaleFactor_BTAG":{"name":"scaleFactor_BTAG", "ptype":"scalar"}, # scaleFactor_BTAG
    "scaleFactor_TRIGGER":{"name":"scaleFactor_TRIGGER", "ptype":"scalar"}, # scaleFactor_TRIGGER
    "scaleFactor_JVFSF":{"name":"scaleFactor_JVFSF", "ptype":"scalar"}, # scaleFactor_JVFSF
    "scaleFactor_ZVERTEX":{"name":"scaleFactor_ZVERTEX", "ptype":"scalar"} # scaleFactor_ZVERTEX
}


#--- Aditional features---#

def get_mtw(event):
    mtw_list = []
    # Llenado de la masa transversa
    for j in range(event.lep_n):
        # Definiciones de TLorentzVector
        Lepton = ROOT.TLorentzVector()
        MeT = ROOT.TLorentzVector()
        # Llenar los vectores de Lorentz
        Lepton.SetPtEtaPhiE(event.lep_pt[j], event.lep_eta[j], event.lep_phi[j], event.lep_E[j])
        MeT.SetPtEtaPhiE(event.met_et, 0.0, event.met_phi, event.met_et)
        # Cálculo de mTW usando TLorentz vectors
        cos_delta_phi = ROOT.TMath.Cos(Lepton.DeltaPhi(MeT))
        mTW = ROOT.TMath.Sqrt(2.0 * Lepton.Pt() * MeT.Et() * (1 - cos_delta_phi))
        # Llenado de la masa
        mtw_list.append(mTW)
    
    return mtw_list

ADD_FEATURES = {
    # Track isolation ratio
    "track_isolation": lambda event: [event.lep_ptcone30[j] / event.lep_pt[j] for j in range(event.lep_n)], 
     # Cluster isolation ratio
    "cluster_isolation": lambda event: [event.lep_etcone20[j] / event.lep_pt[j] for j in range(event.lep_n)],
    # Numero de b-jets
    "b_jet_n": lambda event: len([event.jet_pt[j] for j in range(event.jet_n) if event.jet_mv1[j]>=0.7892]),
    # Masa transversa W
    "mtw" : get_mtw,
    # scaleFactor
    "scaleFactor": lambda event: np.prod([getattr(event, key) for key in event.index if "scaleFactor" in key]),
    # event weight
    "evtw": lambda event: np.prod([getattr(event, key) for key in event.index if "scaleFactor" in key])*event.mcWeight
}


#--- Reglas de selección de eventos ---#
def cut_rules(event):
    # cortes en blanco
    cuts = np.zeros(8, dtype=int)

    # 1. corte de buen vertice
    cuts[0] = event.good_vertex

    # 2. corte de lepton trigger
    cuts[1] = 1 if (event.trig_e==1 or event.trig_m==1) and cuts[0]==1 else 0

    # 3. corte de un unico buen lepton
    for i in range(event.lep_n):
        if event.lep_pt[i] >= 25000 and event.track_isolation[i] < 0.15 and event.cluster_isolation[i] < 0.15:
            if event.lep_type[i] == 13 and abs(event.lep_eta[i]) <= 2.5:
                cuts[2] += 1
            elif event.lep_type[i] == 11 and abs(event.lep_eta[i]) <= 2.47 and (abs(event.lep_eta[i])<= 1.37 or abs(event.lep_eta[i]) >= 1.52 ):
                cuts[2] += 1
    cuts[2] = 1 if cuts[2] == 1 and cuts[1]==1 else 0

    # 4. corte de por lo menos 4 jest
    cuts[3] = 1 if event.jet_n >= 4 and cuts[2] == 1 else 0

    # 5. corte por 4 buenos jets
    for i in range(event.jet_n):
        if event.jet_pt[i] >= 50000 and abs(event.jet_eta[i]) < 2.5:
            cuts[4] += 1
        elif event.jet_pt[i] >= 25000 and abs(event.jet_eta[i]) < 2.4 and event.jet_jvf[i] > 0.5:
            cuts[4] += 1
    cuts[4] = 1 if cuts[4] >= 4 and cuts[3]==1 else 0

    # 6. por lo menos 2 b-jets
    for i in range(event.jet_n):
        cuts[5] += 1 if event.jet_mv1[i] >= 0.7892 else 0
    cuts[5] = 1 if cuts[5] >= 2 and cuts[4]==1 else 0

    # 7. energia perdida
    cuts[6] = 1 if event.met_et >= 30000 and cuts[5]==1 else 0

    # 8. masa transversa del w
    cuts[7] = 1 if any(x >= 30000 for x in event.mtw) and cuts[6]==1 else 0

    return cuts

#--- Histogramas ---#

# Función para crear los histogramas ttbar
def create_hist(sub_fix="after cuts"):
    # Histograms
    histograms = {}

    # Histogramas vacios para variables leptonicas
    histograms["leptons_num"] = ROOT.TH1F(f"leptons_num", f"Total leptons {sub_fix}; Lepton multiplicity ; Events", 14, -1, 6)
    histograms["leptons_pt"] = ROOT.TH1F(f"leptons_pt", f"Leptons pT {sub_fix}; pT(GeV); Events", 60, 0, 120)
    histograms["track_isol"] = ROOT.TH1F(f"track_isol", f"Track isolation {sub_fix}; Isolation (%) ; Events", 70, -0.1, 0.6)
    histograms["calor_isol"] = ROOT.TH1F(f"calor_isol", f"Calorimeter isolation {sub_fix}; Isolation (%) ; Events", 70, -0.1, 0.6)
    histograms["eta_lepton"] = ROOT.TH1F(f"eta_lepton", f"Eta lepton {sub_fix}; eta ; Events", 50, -3, 3)

    # Histogramas vacios para variables de jets
    histograms["jets_num"] = ROOT.TH1F(f"jets_num", f"Total jets {sub_fix}; Jet multiplicity ; Events", 14, -1, 6)
    histograms["jets_pt"] = ROOT.TH1F(f"jets_pt", f"Jest pT {sub_fix}; pT(GeV); Events", 60, 0, 120)
    histograms["eta_jets"] = ROOT.TH1F(f"eta_jets", f"Eta jets {sub_fix}; eta ; Events", 50, -3, 3)
    histograms["jvf_jets"] = ROOT.TH1F(f"jvf_jets", f"JVF Jets {sub_fix}; JVF ; Events", 50, 0, 1)
    histograms["mv1_jets"] = ROOT.TH1F(f"mv1_jets", f"MV1 Jets {sub_fix}; MV1 ; Events",50 , 0, 1)
    histograms["b_jets_num"] = ROOT.TH1F(f"b_jets_num", f"Total b-Jets {sub_fix}; Jets (#) ; Events", 14, 0, 6)

    # Histogramas de energía perdida
    histograms["met_et"] = ROOT.TH1F(f"met_et", f"MET {sub_fix}; GeV; Events", 60, 0, 120)
    histograms["mtw"] = ROOT.TH1F(f"mtw", f"MTW {sub_fix}; GeV; Events", 60, 0, 160)

    # Histogramas de weights
    histograms["mc_weight"] = ROOT.TH1F(f"mc_weight", f"MC Weight {sub_fix}; weight; Events", 100, -0.1, 1.1)
    histograms["mc_weight_sf"] = ROOT.TH1F(f"mc_weight_sf", f"MC Weight factor scaled {sub_fix}; weight; Events", 100, -0.1, 1.1)

    return histograms

#Función para llenar los histogramas ttbar
def fill_hist(histograms, event, mc=True):
    # Define weight
    evtw = event.evtw if mc else 1
    # Histogramas vacios para variables leptonicas
    histograms["leptons_num"].Fill(event.lep_n,evtw)
    for i in range(event.lep_n):
        histograms["leptons_pt"].Fill(event.lep_pt[i]/1000,evtw)
        histograms["track_isol"].Fill(event.track_isolation[i],evtw)
        histograms["calor_isol"].Fill(event.cluster_isolation[i],evtw)
        histograms["eta_lepton"].Fill(event.lep_eta[i],evtw)
        histograms["mtw"].Fill(event.mtw[i]/1000,evtw)

    # Histogramas vacios para variables de jets
    histograms["jets_num"].Fill(event.jet_n,evtw)
    histograms["b_jets_num"].Fill(event.b_jet_n,evtw)
    for i in range(event.jet_n):
        histograms["jets_pt"].Fill(event.jet_pt[i]/1000,evtw)
        histograms["eta_jets"].Fill(event.jet_eta[i],evtw)
        histograms["jvf_jets"].Fill(event.jet_jvf[i],evtw)
        histograms["mv1_jets"].Fill(event.jet_mv1[i],evtw)

    # Histogramas adicionales
    histograms["met_et"].Fill(event.met_et/1000,evtw)
    histograms["mc_weight"].Fill(event.mcWeight)
    histograms["mc_weight_sf"].Fill(event.evtw)

    return histograms
