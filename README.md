# GRB_TSNE
Using t-SNE to classify GRBs from the Swift catalogue. 

The code is built up by modules so that each could be replaced with another procedure and not have to redo the rest if someone wants to take that on. 

We publish the code for free use.

The flow is.

getting_required_files which will be observatory specific.

generating_dataset should process the lightcurves (LCs)

config.py should be changed for the parameters one wants to make the embedding with (embedding.py) and plot (plotting.py).

table_gen and write_fits are just nice-to-have in case anybody would like to make a nice table with results for the community

Updated in April 2021 with a tentative example of how to download BATSE files
