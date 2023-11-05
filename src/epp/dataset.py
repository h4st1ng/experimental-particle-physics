# Module to get and set root data

import ROOT


def get_dataset(dir=''):
    """
    Abre un archivo ROOT y obtiene un árbol (tree) específico del archivo.

    Args:
        dir (str): Ruta al archivo ROOT que se va a abrir.
        name (str): Nombre del árbol (tree) que se va a obtener.

    Returns:
        TTree: El árbol (tree) obtenido del archivo ROOT.

    Example:
        Para abrir un archivo 'mi_archivo.root' y obtener el árbol 'mi_tree':
        dataset = get_dataset('mi_archivo.root', 'mi_tree')
    """
    f = ROOT.TFile.Open(dir)

    return f