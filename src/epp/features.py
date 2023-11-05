# Modulo para generar features

import pandas as pd
import ROOT


def instance_selection(event,cut_rules):
    return cut_rules(event)


def feature_adition(event,features):
    try:
        for key in features:
            event[key] = features[key](event)
    except:
        None
    return event


def feature_extraction(event, features):

    # Crear dataframe de variables
    data = {}
    for key in features:
        if features[key]["ptype"]=="scalar": 
            data[features[key]["name"]] = getattr(event, key)
        elif features[key]["ptype"]=="vector": 
            data[features[key]["name"]] = [x for x in getattr(event, key)]
    df_features = pd.Series(data)

    return df_features