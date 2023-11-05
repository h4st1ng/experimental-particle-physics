#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Modulos de desarrollo
import os
import time
import datetime
import ROOT

# Modulos de aplicación
from src.epp.dataset import get_dataset
from src.epp.features import feature_extraction, feature_adition, instance_selection
from src.epp.utils import parser_param, save_histogram
# Global config
from config import DATA_PATH, OUTPUT_PATH


# --- Report config --#
report_name = parser_param("report")
report = report_name
exec(f'from src.epp.reports import {report} as report')


def main():
    # Traer datos
    f = get_dataset(DATA_PATH+report.DATASET_NAME)
    tree = f.Get(report.TREE_NAME)
    print(f"{datetime.datetime.now()}: Archivo cargado. Total de eventos: {tree.GetEntries()}")

    # Crear histogramas
    histograms = report.create_hist()
    cuts_hist = ROOT.TH1F("Cuts", f"Total event cuts; Passed cuts ; Events", 20, -1, 10)
    print(f"{datetime.datetime.now()}: Histogramas creados: {len(histograms)+1}")

    # Loop
    print(f"{datetime.datetime.now()}: Inicio del loop")
    total_events = 0
    for i, event in enumerate(tree):
        # Print state
        if (i+1)%int(tree.GetEntries()*0.1) == 0:
            print(f"{datetime.datetime.now()}: Avance: {round(100*(i+1)/tree.GetEntries(),2)}%")
        # Extracción de variables
        event = feature_extraction(event=event, features=report.RAW_FEATURES)
        # Adición de features
        event = feature_adition(event=event, features=report.ADD_FEATURES )
        # Selección de eventos
        cuts = instance_selection(event, report.cut_rules)
        # Fill cut histogram
        for i in range(cuts.sum()): cuts_hist.Fill(i)
        # Fill principal histograms
        if cuts.sum()==cuts.shape[0]:
            total_events += 1
            histograms = report.fill_hist(histograms, event)
    # final state
    print(f"{datetime.datetime.now()}: fin del loop")
    print(f"     --- Total events: {tree.GetEntries()}")
    print(f"     --- Total efective events: {total_events}")

    # Saver directory
    hist_path = OUTPUT_PATH+report_name+"/"
    if not os.path.exists(hist_path):
        os.makedirs(hist_path)
    # Save histograms
    save_histogram(histogram=cuts_hist, path_file= hist_path + "cuts.root")
    for key in histograms:
        path_file = hist_path + f"{key}.root"
        save_histogram(histogram=histograms[key], path_file= path_file)
    print(f"{datetime.datetime.now()}:// HIstogramas guardados en {hist_path}")


if __name__ == "__main__":
    main()