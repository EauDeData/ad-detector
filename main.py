import json 
import os

import src.offline.detection as det

config = json.load(open('src/config.json'))
offline_process = config['precalculate']
filenames = config['filenames']
files = config['kword_files']
target = config['target']


#### OFFLINE STUFF ####
if not os.path.exists(filenames): raise AssertionError(f"Filenames file not found in {filenames}, ensure there's such file with the absolute path to each PDF.")


if offline_process:
    
    #### DETECTION STEP ###
    det.compute(filenames)

    import src.offline.precalculate_kwords as kws
    import src.offline.prepare_images as prep

    names = ["matrimonials_punts.json", 'matrimonials_adjectius.json', 'matrimonials_idioms.json']

    print("Precalculating keywords...")
    kws.precalculate(files, names)
    
    print("Precalculating images...")
    # TODO: Obliterate target before calling the function
    prep.prepare(filenames, target)

import src.gui.gui as gui

interface = gui.GUI(target, data_path=filenames)
interface.mainloop()





