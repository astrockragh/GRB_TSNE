'''Swift specific but good foe inspirations'''
import numpy as np
import pandas as pd
import os

# Read files
duration_data = pd.read_pickle('DataFrames/duration_data.dat')
fluence_data = pd.read_pickle('DataFrames/fluence_data.dat')


def cut_norm_lc(filename): #Prepare single light curve, cut to T100 and normalize by fluence
    grbname = filename[12:-7]
    #Cut lightcurve
    lc = pd.read_csv(filename, sep = ' ', header = None)
    lc = lc.loc[:, [0, 1, 3, 5, 7]]
    lc = lc.loc[lc.loc[:,0].apply(lambda x: duration_data.T100_start[grbname] <= x and x <= duration_data.T100_end[grbname])]
    lc.reset_index(drop=True,inplace=True)
    lc = lc.iloc[:,[1,2,3,4]] / float(fluence_data[grbname])
    return len(lc), lc # Return length and the cutted lightcurve
    


def prepare_lcs():
    # Go thorugh all LightCurves in the folder Light Curve and prepare them
    path = "LightCurves/"
 
    unpadded_curves = []
    grbnames = []
    errors = []

    # Go through all the files
    max_len = 0 # Record longest burst
    count = 1

    error_log = ""

    for file in os.listdir(path):
        try: 
            if count % 100 == 0:
                print(f"{count} files done")
            count += 1
            length, lc = cut_norm_lc(path + file)
            if length <= 1:
                error_log += f"{file[:-7]} \t Too short \n"
                continue
            unpadded_curves.append(lc)
            grbnames.append(file[:-7])
            if length > max_len:
                max_len = length
        except: # If we recieve an error we log it
            errors.append(file)
            error_log += f"{file[:-7]} \t Couldn't cut and normalize \n"
            print(f"error with {file}")
        # os.remove(path + file)
    
    # save backup for debugging purposes
    print("LightCurves normalised and cut")
    pd.to_pickle([unpadded_curves, grbnames, errors, max_len], "backup.dat")

    # Load backup
    # (unpadded_curves, grbnames, errors, max_len) = pd.read_pickle("backup.dat")

    prepared_lcs = []

    # Go through and pad
    count = 0
    for lc in unpadded_curves:
        temp = np.zeros(shape = (max_len, 4))
        temp[:len(lc), :] = lc
        prepared_lcs.append(temp.reshape(-1))

        if count % 100 == 0:
            print(f"{count} lightcurves padded")

    del unpadded_curves

    # Make to DataFrame
    prepared_dataset = pd.DataFrame(prepared_lcs)
    prepared_dataset.index = grbnames[:len(prepared_dataset)]
    prepared_dataset.index = grbnames
    prepared_dataset.to_pickle('non_fft_dataset.dat')
    print(prepared_dataset)

     # Write errors to log
    err_file = open("Error_log.txt", "w")
    err_file.write(error_log)
    err_file.close()

if __name__ == "__main__":
    prepare_lcs()