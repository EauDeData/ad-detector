import tkinter as tk
from tkinter import ttk
from io import BytesIO
from PIL import Image, ImageTk
import json
import copy
import os
import numpy as np

import src.process.parse_results as pr
from src.process.dataloader import *
from src.stale_data import LANGS, RESULTS

bow = pr.bow
results = pr.results

def scale(image, factor):

    w, h, _ = image.shape
    s = int(factor * h), int(factor * w)
    
    return cv2.resize(image, s)


class OnClickEventListener:
    def __init__(self, img, main) -> None:
        self.img = ImageTk.PhotoImage(img)
        self.main = main

    def __call__(self, _ = None):
        
        window = tk.Toplevel(self.main)
        window.title("image")
        label = tk.Label(window, image=self.img)
        label.image = self.img

        label.pack()

class ForwardEventListener:
    def __init__(self, func, step) -> None:
        self.func = func
        self.step = step
    
    def __call__(self, _ = None):
        self.func(self.step)

class BBxShowEventListener:
    def __init__(self, img, main,  data, index, lut) -> None:

        self.img = np.array(img)
        self.main = main
        self.data = data
        self.index = index
        self.lut = lut


    def __call__(self, _ = None):
        #### PROCESS NUMPY IMAGE FOR BBXS ###
        fn = self.lut[self.index] # Get idx
        bbxs = [x['bbx'] for x in self.data[fn]]
        self.img = cv2.cvtColor(self.img, cv2.COLOR_GRAY2BGR)
        for bbx in bbxs: cv2.rectangle(self.img, (bbx[0],bbx[1]), (bbx[0] + bbx[2], bbx[1] + bbx[3]), (0, 0, 255), 5)
        self.img = scale(self.img, .25)

        ### NORMAL SHOW ####
        self.img = ImageTk.PhotoImage(Image.fromarray(self.img))
        window = tk.Toplevel(self.main)
        window.title("image")
        label = tk.Label(window, image=self.img)
        label.image = self.img

        label.pack()
    

class StateVariables:
    
    def __init__(self, dataloader, img_prev, img_now, img_next, imh, imw, results_viewport, main, target) -> None:
        self.loader = DataAnuncis(dataloader)

        self.main = main

        ### init showing imgs ###
        self.containers = {0: img_prev, 1: img_now, 2: img_next}
        
        self.imh, self.imw = imh, imw

        self.showing_img_index = 1
        self.img_list = [
            Image.fromarray(self.loader[self.showing_img_index - 1][0]),
            Image.fromarray(self.loader[self.showing_img_index][0]),
            Image.fromarray(self.loader[self.showing_img_index + 1][0])
        ]
        self.image_labels = [0, 0, 0]
        self.fn2idx = {x.strip(): n for n, x in enumerate(self.loader.files)}
        self.idx2fn = {n: x.strip() for n, x in enumerate(self.loader.files)}

        ### results ###
        self.category = 'matrimonials'
        self.results = json.load(open(RESULTS[self.category]))
        self.res_viewport = results_viewport
        self.buffer = {}
        self.target = target
    
    def change_category(self, cat):
        self.category = cat
        self.results = json.load(open(RESULTS[self.category]))
        self.fill_results()

    def tkinterize_images(self):

        for n, imor in enumerate(self.img_list):

            for widget in self.containers[n].winfo_children(): widget.destroy()

            if not isinstance(imor, type(None)):

                im = copy.copy(imor)
                shape = ((int(self.imw//1.5), int(self.imh//1.5))) if n != 1 else (int(self.imw), int(self.imh))
                img = ImageTk.PhotoImage(im.resize(shape))
                label = tk.Label(self.containers[n], image = img)
                label.image = img
                if n!=1: label.bind("<Button-1>", ForwardEventListener(self.forward_image, -1 if not n else 1))
                else:
                    
                    event = BBxShowEventListener(copy.copy(im), self.main, self.results, self.showing_img_index, self.idx2fn)
                    label.bind("<Button-1>", event)

                label.pack()

            else: self.image_labels[n] = None

        return None

    def forward_image(self, index):

        if not (index < 0 and not self.showing_img_index):
            self.showing_img_index += index
            if self.showing_img_index <= 0:
                self.img_list = [
                    None,
                    Image.fromarray(self.loader[0][0]),
                    Image.fromarray(self.loader[1][0])
                ]
                self.showing_img_index = 0
            
            elif self.showing_img_index > len(self.loader):
                
                self.img_list = [
                    Image.fromarray(self.loader[-2][0]),
                    Image.fromarray(self.loader[-1][0]),
                    None
                ]
                self.showing_img_index = len(self.loader) - 1
            
            else:

                if index > 0:
                    self.img_list = self.img_list[1:] + [Image.fromarray(self.loader[self.showing_img_index + 1][0])]
                
                else:
                    self.img_list = [Image.fromarray(self.loader[self.showing_img_index - 1][0])] + self.img_list[:-1]
            
            self.tkinterize_images()
            self.fill_results()

    def fill_results(self):
        print("Filling for category", self.category)
        for widget in self.res_viewport.winfo_children(): widget.destroy()
        path = '{}/{}/{}/'.format(self.target, self.category, self.showing_img_index) # You are doing this in the ugliest way possible; pls refactor everything in a scheme that makes sense and its not done by a first-year noob.
        if os.path.exists(path):

            img_fns = os.listdir(path)
            h, w = 90, 60
            margin = 50
            if not self.showing_img_index in self.buffer:

                imgs = [Image.open(path + img) for img in img_fns]
                sorted(imgs, key=lambda x: img_fns[imgs.index(x)].split('_')[-1])
                imgs = imgs[::-1]
                self.buffer[self.showing_img_index] = imgs
            
            else:

                imgs = self.buffer[self.showing_img_index]
            
            max_per_row = 10
            for n, pilimage in enumerate(imgs):

                tkimage = ImageTk.PhotoImage(pilimage.resize((h, w)))
                but = OnClickEventListener(pilimage, self.main)

                self.canvas = tk.Label(self.res_viewport, image = tkimage)
                self.canvas.image =  tkimage
                self.canvas.bind("<Button-1>", but)
                self.canvas.place(y = margin/2 + (h * (n//max_per_row)), x = margin + (margin + w) * (n%max_per_row))
            


class GUI(tk.Tk):
    def __init__(self, target, height = 900, width = 1200, margin = 5, lang = 'cat', imh = 440, imw = 320, data_path = '/home/adri/Desktop/cvc/tinder-historic/data/filenames.txt', *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)

        ### PARAMS ###
        self.h, self.w = height, width
        self.margin = margin
        self.lang = lang

        self.imh = imh
        self.imw = imw

        ### LAYOUT ###
        self.set_layout()

        ### STATE VARIABLES ###
        self.state = StateVariables(data_path,
                    self.prev_image_container,
                    self.showing_image_container,
                    self.next_image_container,
                    self.imh, self.imw,
                    self.dataset_container,
                    self,
                    target)

        ### ROOT ###
        self.set_root()

        #### PACKING ####
        self.pack_elements()
        self.state.tkinterize_images()
        self.state.fill_results()

    def set_root(self):
        self.geometry(f"{self.w}x{self.h}")
        self.resizable(False, False)
        self.title("Detector d'Anuncis")

    def set_layout(self):

        color = 'azure'

        self.kwords_container = tk.Frame(self, height=self.h//1.5, width=self.w//4, bg = color)
        self.dataset_container = tk.Frame(self, height=self.h - (self.h//1.5 + 3 * self .margin), width=(self.w - 2 * self.margin), bg = "grey83")
        self.results_container = tk.Frame(self, height=self.h//1.5, width=self.w - (self.w//4 + 3 * self.margin), bg = color)

        self.showing_image_container = tk.Frame(self.results_container, height =  self.imh + self.margin, width = self.imw + self.margin, bg = "white")

        self.prev_image_container = tk.Frame(self.results_container, height =  self.imh//1.5 + self.margin, width = self.imw//1.5 + self.margin, bg = "white")
        self.next_image_container = tk.Frame(self.results_container, height =  self.imh//1.5 + self.margin, width = self.imw//1.5 + self.margin, bg = "white")
    
        self.checkboxes = []
        
        matrimonials_check = ttk.Button(self.kwords_container, text=LANGS['matrimonials'][self.lang], command=lambda: self.state.change_category('matrimonials'))
        self.checkboxes.append(matrimonials_check)

        adj = ttk.Button(self.kwords_container, text=LANGS['adjectius'][self.lang], command=lambda: self.state.change_category('adjectius'))
        self.checkboxes.append(adj)

        idioms = ttk.Button(self.kwords_container, text=LANGS['idioms'][self.lang], command=lambda: self.state.change_category('idioms'))
        self.checkboxes.append(idioms)

    def pack_elements(self):
        self.kwords_container.place(x = self.margin, y = self.margin)

        y = self.h//1.5 + 2 * self.margin
        self.dataset_container.place(x = self.margin, y = y)

        x = self.w // 4 + 2 * self.margin
        self.results_container.place(y = self.margin, x = x)


        yim = (self.h//1.5) // 2 - (self.imh//2 + 2 * self.margin)
        xim = (self.w - (self.w//4 + 3 * self.margin)) // 2 - (self.imw//2 + 2*self.margin)
        self.showing_image_container.place(x = xim, y = yim)

        y = yim + self.imh // 4
        x = xim - (self.imw//1.5 + self.margin * 2)
        self.prev_image_container.place(x = x, y = y)

        x = xim + self.imw + self.margin * 2
        self.next_image_container.place(y = y, x = x)

        for n, check in enumerate(self.checkboxes): check.place(x = self.margin, y = self.margin + n * self.margin * 5)


if __name__ == '__main__':
    g = GUI()
    g.mainloop()