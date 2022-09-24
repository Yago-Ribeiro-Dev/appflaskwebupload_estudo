from itertools import zip_longest
import os
import sys
import pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError)
import cv2
import numpy as np
import re
import pandas as pd
from datetime import datetime
import pytesseract
from config import UPLOADFOLDER
import os
import csv
from flask import current_app
from itertools import groupby
from collections import Counter


class Viscardi:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    def __init__(self,path):
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '21'
        self.listadicts = []

    def converter_imgpdf(self):
     
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/viscardi'+ str(i) +'.jpg', 'JPEG')
            print(images[i])
    
    def search_files(self):
        imagem = [x for x in os.listdir(self.imagem) if 'viscardi']
        return imagem
    
    def get_referencias(self, sku):
        return str(sku['SKU'].strip())


    def reader_imagem(self):
        search_valores = re.compile(r'\s\d+\s\d+\,\d+')
        imagens = self.search_files()
        try:
            for imagem in imagens:
                file = cv2.imread(os.path.join(self.imagem,imagem))
                
                imagemgray = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)

                texto = pytesseract.image_to_string(imagemgray, lang= self.tesseract_language,config=self.config)
                valores = texto.split('\n')
                for valor in valores:
                    remov = re.sub('[A-Z]+\s+[A-Z]|\s+',' ', valor)
                    remov = remov.strip().split(" ")
                    cont = len(remov)
                    if cont >1:
                        dict_items = {}
                        
                        sku = remov[-2]
                        saldo = remov[-1]
                        try:
                            dict_items['SKU'] = str('Viscardi-') + str(sku).strip()
                        except:
                            dict_items['SKU'] = 'notfound'

                        try:
                            num = str(saldo).replace(',','.').strip()
                            dict_items['SALDO'] = round(float(num),2)
                        except:
                            dict_items['SALDO'] = float(0)

                       # dict_items['IDMARCA'] = self.idmarca
                        self.lista_produtos.append(dict_items)
                       
        except:
            pass
     
    
    def add_column(self, *args, **kwargs):
        for arg in args:
            x = {"IDMARCA":self.idmarca}
            arg.update(x)
            return arg


    def group_by(self):
        key = lambda d: d['SKU']

        SALDO = []
        for SKU,grps in groupby(sorted(self.lista_produtos, key=key), key=key):

            c = Counter()
            for grp in grps:
                grp.pop('SKU')
                c += Counter(grp)

            SALDO.append(dict(c, SKU=SKU))
        dicts = list(map(self.add_column,SALDO))
        return dicts
       



