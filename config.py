#config for plotting. note the highlights for special bursts

import pandas as pd
import numpy as np

embedding = np.genfromtxt('embedding.csv', delimiter=',',dtype=str)
grbnames = embedding[:,0]
duration_data = pd.read_pickle('DataFrames/duration_data.dat')

conf = {
    'figsize': (12, 8),
    'radius': 5,
    'color': np.log(duration_data.loc[grbnames].T90),
    'cmap': 'plasma',
    'grb_highlight': ['GRB191019A']
}

tsne_params = {
    'perplexity':  35,
    'verbose':     2,  
    'n_iter':   15000,
}