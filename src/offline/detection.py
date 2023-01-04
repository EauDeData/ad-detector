import cv2
import numpy as np
import matplotlib.pyplot as plt
import json 
import multiprocessing as mp

from src.process.dataloader import *

from pytesseract import Output
import pytesseract


def string_to_bag_of_chars(string):

    base = [0 for _ in range(256)]
    for l in string: base[ord(l)] += 1 

    return base


def ad_contours_mp(boxes_bbx, contours, hierarchy, thread, num_threads):


        
    for n in range(thread, len(contours), num_threads):
        c = contours[n]
        if hierarchy[0][n][-2] == -1: continue
        rect = cv2.boundingRect(c)
        if rect[2] < 100 or rect[3] < 100: continue
        x,y,w,h = rect
        # cv2.rectangle(copied,(x,y),(x+w,y+h),(255, 0, 0),2)
        boxes_bbx[n] = (x, y, w, h)

    return None




def ad_detector(img):

    # copied = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)

    # Processing operations
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV) # Letters (1) Background (0)
    dst = cv2.cornerHarris(thresh,10,3,0.04)
    dst = (dst - dst.min()) / (dst.max() - dst.min()) * 255
    ret, thresh = cv2.threshold(dst.astype(np.uint8), 0, 255, cv2.THRESH_OTSU)

    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))
    blops = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, blops)
    horizontal = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, horizontalStructure.T)

    contours, hierarchy = cv2.findContours(horizontal, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    boxes_bbx = [0 for i in range(len(contours))]
    threads = 8

    L = mp.Manager().list(boxes_bbx)
    processes = [mp.Process(target = ad_contours_mp, args=(L, contours, hierarchy, i, threads)) for i in range(threads)]
    [p.start() for p in processes]
    [p.join() for p in processes]


    return list(L)

def crop_words(bbx):
    
    d = pytesseract.image_to_data(bbx, lang = 'spa', nice = 5, output_type=Output.DICT)
    n_boxes = len(d['level'])
    text = []
    
    for i in range(n_boxes):

        detection = d['text'][i]
        if len(detection)!=0: text.append(detection)
    
    return text

def ad_to_json(bbx):

    words = crop_words(bbx)

    return words

def file_to_json(doc):

    bbxs = ad_detector(doc)

    res = {}
    for n, bbx in enumerate(bbxs):
        if not bbx: continue
        x, y, h, w = bbx
        res[n] = {"ocr": ad_to_json(doc[y:y+h, x:x+w]), 'bbx': bbx}
    
    return res

def all_files_json(dataloader):

    json_collection = {"files": {}}

    for num_document in range(len(dataloader)):

        print(f"Processant {num_document}\t",)

        document = dataloader[num_document][0]
        name = dataloader.files[num_document].strip()

        json_collection['files'][num_document] = {'filename': name, 'ads': file_to_json(document)}

    return json_collection

def compute(filenames):
    files = DataAnuncis(filenames)
    json_all = all_files_json(files)
    with open("./src/jsons/results.json", "wb") as outfile:
        string = json.dumps(json_all)
        outfile.write(string.encode('utf-8'))
