# Herramientas auxiliares

import argparse
import ROOT

from reportlab.lib.pagesizes import letter
from reportlab.lib import utils
from reportlab.platypus import SimpleDocTemplate, Image

def export_png_as_pdf(image_paths,pdf_filename):
    # Crear un archivo PDF
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Crear una lista de elementos para agregar al PDF
    elements = []

    # Agregar las imágenes al PDF
    for image_path in image_paths:
        img = utils.ImageReader(image_path)
        width, height = img.getSize()
        aspect_ratio = width / height

        # Puedes ajustar el tamaño de la imagen como desees
        max_width = 400  # Cambia esto según tus necesidades
        img_width = min(max_width, width)
        img_height = img_width / aspect_ratio

        image = Image(image_path, width=img_width, height=img_height)
        elements.append(image)

    # Construir el PDF
    doc.build(elements)

    print(f'Se ha creado el archivo PDF: {pdf_filename}')




def parser_param(parametro):
    # Configura el analizador de argumentos
    parser = argparse.ArgumentParser(description='Descripción de tu script')
    # Agrega argumentos
    parser.add_argument('--' + parametro, type=str, help='Descripción del parámetro')
    # Parsea los argumentos de la línea de comandos
    args = parser.parse_args()
    # Accede a los valores de los argumentos
    param_value =  getattr(args, parametro)

    return param_value

def save_histogram(histogram, path_file):
    # Crea un archivo ROOT para guardar el histograma
    file = ROOT.TFile(path_file, "RECREATE")
    # Guarda el histograma en el directorio actual
    histogram.Write()
    # Cierra el archivo ROOT
    file.Close()