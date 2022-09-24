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


#https://stackoverflow.com/questions/57567297/sum-of-key-values-in-list-of-dictionary-grouped-by-particular-key
class Elizabeth:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def __init__(self, path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.lista_produtos = []
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
       
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M')).split()[0]
        self.idmarca = '14'
   
    def converter_imgpdf(self):
     
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/elizabeth'+ str(i) +'.jpg', 'JPEG')
            print(images[i])


    def reader_imagem(self):
        imagens = os.listdir(self.imagem)
      
        lista_saldos = []
        for imagem in imagens:
            if 'elizabeth' in imagem:
                print(imagem)

                img = cv2.imread(os.path.join(self.imagem, imagem))
                imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                valores = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                valores = valores.split('\n')
                for valor in valores:
                    dict_item = {}
                    x = valor.find('0104')
                    y = valor.find('0101')
                    sep = valor[x:].split()
                    if x >0:
                        try:
                            
                            sku = sep[0]
                            saldo = sep[-1]
                            dict_item['SKU'] = str(sku).replace("0104","104")
                            if len(saldo) <=9:
                                dict_item['SALDO'] = round(float(str(saldo).replace(".","").replace(",",".")),2)
                            else:
                                dict_item['SALDO'] = 0
                     
                            lista_saldos.append(dict_item)
                            self.lista_produtos.append(dict_item)
                           
                        except:
                            pass

                   
                    elif y >0:
                        try:
                            sku = sep[0]
                            saldo = sep[-1]
                            dict_item['SKU'] = sku
                            if len(saldo) <= 9:

                                dict_item['SALDO'] = round(float(str(saldo).replace(".","").replace(",",".")),2)
                            else:
                                dict_item['SALDO'] = 0
                            
                            self.lista_produtos.append(dict_item)

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
      
        return [x for x in dicts]
        
       