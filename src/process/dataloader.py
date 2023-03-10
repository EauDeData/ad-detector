from asyncore import read
import pdf2image
import numpy as np
import cv2
from PyPDF2 import PdfFileReader

def TranslatePoints(src, srcSize, dstSize):
    sx0, sy0, sx1, sy1 = src
    _, _, ssx, ssy = srcSize
    dsy, dsx = dstSize

    dx0 = sx0 / ssx * dsx
    dx1 = sx1 / ssx * dsx
    dy0 = sy0 / ssy * dsy
    dy1 = sy1 / ssy * dsy
    return dx0, dsy - dy0, dx1, dsy - dy1


def read_img(path):
    img = pdf2image.convert_from_path(path.strip())
    assert len(img) == 1, f"En teoria tot té una sola pàgina, error a: {path} on hi han {len(img)}"
    return np.array(img[0])

class DataAnuncis:
    def __init__(self, filenames) -> None:
        self.files = open(filenames, 'r').readlines()
        self.resize = False
        self.queue = {n: self.get(n) for n in range(15)}
    
    def __len__(self):
        return len(self.files)
    
    def get(self, index):
        try:
            fn = self.files[index].strip()
            reader = PdfFileReader(fn)
            GT = []
            img = cv2.cvtColor(read_img(fn), cv2.COLOR_RGB2GRAY)
            for page in reader.pages:
                for annot in page["/Annots"] :
                    rect = annot.getObject()['/Rect']
                    points = TranslatePoints(rect, page.mediaBox, img.shape)
                    if points[0] < img.shape[1] and points[1] < img.shape[0]: GT.append(points)

            return img, GT, fn
        except KeyError:
            fn = self.files[index].strip()
            reader = PdfFileReader(fn)
            GT = []
            img = cv2.cvtColor(read_img(fn), cv2.COLOR_RGB2GRAY)
            return img, 0, fn

    def __getitem__(self, index):
        if not index in self.queue:
            self.queue = {n: self.get(n) for n in range(index, min(index+5, len(self)))}
        toret = self.queue[index]
        if len(self.queue) > 50: self.queue = {}
        return toret



    
    def loop(self):
        for file in self.files:
            yield read_img(file)
