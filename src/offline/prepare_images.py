from src.process.dataloader import *
import os
import cv2
import json

def prepare(filenames, target):
    data = DataAnuncis(filenames)

    if not os.path.exists(target): os.mkdir(target)

    fn2idx = {x.strip(): n for n, x in enumerate(data.files)} 

    results_kinds = ['matrimonials_punts.json',  'matrimonials_adjectius.json', 'matrimonials_idioms.json']
    names = ['matrimonials', 'adjectius', 'idioms']
    
    for cat, res in zip(names, results_kinds):

        results = json.load(open('./src/jsons/' + res))

        for fn in results:

            print(fn)
            idx = fn2idx[fn]
            path = target + f"{cat}/{idx}/"
            try: 
                if os.path.exists(path): os.rmdir(path)
                os.mkdir(path)
            except FileNotFoundError:
                os.mkdir(target + f"{cat}/")
                os.mkdir(path)

                
            print(fn)
            try:
                image = data[idx][0]
            except:
                print("Error!")
                continue
            for n, ad in enumerate(results[fn]):

                x, y, w, h = ad['bbx']
                punts = ad['punts']

                if punts > 1:
                    fnn = path + f"{n}-{punts}.png"
                    cv2.imwrite(fnn, image[y:y+h, x:x+w])
