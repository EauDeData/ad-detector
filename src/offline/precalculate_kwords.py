import src.process.parse_results as pr
import json

bow = pr.bow
results = pr.results

def precalculate(files, names):

    for name_saving, file in zip(names, files):
        sentences = open(file, 'r').readlines()
        bag = set()
        for stnc in sentences:

            words = stnc.strip().replace('+', '').split()
            for w in words: bag.add(w)

        all_ads = [] # Some ads will be several times,
        # el nombre d'aparicions hauria de ser una primera aproximació
        # Podriem millorar amb ANDs i ORs però nem per feina

        for n, word in enumerate(bag):
            print(n, '\t', end = '\r')

            try:
                if len(word) > 3: # Mesura d'optimització, s'hauria de borrar
                    all_ads.extend(pr.find_compatible_ads(pr.closest_words(word, bow, k = 2), results))
            except IndexError: continue
    
        index = {}
        for n, ad in enumerate(all_ads):
            print(n, '\t', end = '\r')
            name = list(ad.keys())[0]
            value = ad[name]
            x, y, w, h = ad[name]['bbx']
            
            if name not in index:
                value['punts'] = 1
                index[name] = [value]
            else:
                appear = 0
                for ad_index in index[name]:
                    x_, y_, w_, h_ = ad_index['bbx']
                    if x_ == x and y_ == y and w_ == w and h_ == h:
                        ad_index['punts'] += 1
                        appear = 1
                        break
                if not appear:
                    value['punts'] = 1
                    index[name].append(value)


        with open('./src/jsons/' + name_saving, "wb") as outfile:
                string = json.dumps(
                    index,
                )
                outfile.write(string.encode('utf-8'))
