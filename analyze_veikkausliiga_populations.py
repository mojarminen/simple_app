# -*- coding: utf-8 -*-

import os
import pickle

main_folder = os.path.dirname(os.path.abspath(__file__))
populations_folder = os.path.join(main_folder, 'populations_veikkausliiga')

files = [f for f in os.listdir(populations_folder) if f.endswith('.pickle')]
files.sort()

current_best = None

for filename in files:
    filepath = os.path.join(populations_folder, filename)
    
    with open(filepath, 'rb') as f:
        try:
            population = pickle.load(f)
            for o in population:
                if current_best is None or current_best[1] < o[1]:
                    current_best = o
                        
            values = [o[1] for o in population]
            
            print filename, ':', sum(values)/len(values)
        except EOFError:
            print filename, ':', 'still open for writing'

print 'Current best:', current_best
