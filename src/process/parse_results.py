import json
import os
import numpy as np
import string
from scipy.spatial import distance
import cv2
import matplotlib.pyplot as plt

from src.process.dataloader import *

printable = set(string.printable)

def string_to_bag_of_chars(word):

    base = np.zeros(256).tolist()
    for l in word:
        if ord(l) < 256: base[ord(l)] += 1


    return base

results = json.loads(open('./src/jsons/results.json', 'r').read())

def get_bow(results):

    bow = {}
    lenght = len(results['files'])
    for n, document in enumerate(results['files']):
        print(f"BOW in document: {n} / {lenght}\t", end = '\r')
        for ad in results['files'][document]['ads']:
            for word in results['files'][document]['ads'][ad]['ocr']:
                if not word in bow:
                    bow[word] = string_to_bag_of_chars(word)
    print("\nBOW already computed")
    return bow

try:
    bow = json.loads(open('./src/jsons/bag_of_words.json', 'r').read())
except:
    bow = get_bow(results)
    open('./src/jsons/bag_of_words.json', 'w').write(json.dumps(bow))

def distance_strings(x, y):
    return sum([abs(i - j) for i,j in zip(x, y)])

def closest_words(word, bow, k = 10):

    bow_list = list(bow.keys())
    vector = string_to_bag_of_chars(word)

    return sorted(bow_list, key = lambda x: distance_strings(bow[x], vector))[:k]
    
def find_compatible_ads(words_to_search, results):

    ads_list = []
    lenght = len(results['files'])
    for n, document in enumerate(results['files']):
        print(f"LUT in document: {n} / {lenght}\t", end = '\r')
        for ad in results['files'][document]['ads']:
            
            text = results['files'][document]['ads'][ad]['ocr']
            if len([x for x in text if x in words_to_search]):
                ads_list.append({results['files'][document]['filename']: results['files'][document]['ads'][ad]})
    print()
    return ads_list

def find_multiple_words(words, result, bow):
    words_to_search = []
    for word in words:
        words_to_search += closest_words(word, bow)
    words_to_search = list(set(words_to_search))
    return find_compatible_ads(words_to_search, result)


def return_detected_pages(compatible_ads_list):

    filenames = {}
    for ad in compatible_ads_list:
        for filename in ad: # Fix: this is just one
            if not filename in filenames: img = read_img(filename)
            else: img = filenames[filename]

            x, y, w, h = ad[filename]['bbx']
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 5)
            filenames[filename] = img

    return list(filenames.values())
