''''code to make the map itself'''

import numpy as np
import pandas as pd
from sklearn.manifold import TSNE

#loading data
non_fft_dataset = pd.read_pickle('non_fft_dataset.dat')

#taking Fast Fourier Transform
fft = np.fft.rfft(non_fft_dataset)

#running t-SNE, n_iter should be higher than 'n_termination'
from config import tsne_params
verbose, perplexity, n_iter = tsne_params['verbose'], tsne_params['perplexity'], tsne_params['n_iter']
emb = TSNE(verbose = verbose, perplexity = perplexity, n_iter = n_iter).fit_transform(abs(fft))

#saving dataset, change name at will
np.savetxt("embedding.csv",np.vstack((non_fft_dataset.index, emb[:,0], emb[:,1])).T, delimiter = ',',fmt='%s')