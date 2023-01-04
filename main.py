import src.offline.detection as det


#TODO: Read everything from config file
offline_process = 0 # TODO: As parameter
filenames = '/home/adri/Desktop/cvc/tinder-historic/data/filenames.txt'
files = ['/home/adri/Desktop/cvc/tinder-historic/data/kwords/matrimonials_full.txt',
        '/home/adri/Desktop/cvc/tinder-historic/data/kwords/matrimonials_adjectius.txt',
        '/home/adri/Desktop/cvc/tinder-historic/data/kwords/matrimonials.txt']
target = '/home/adri/Desktop/cvc/tinder-historic/data/prepared/'


#### OFFLINE STUFF ####


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





