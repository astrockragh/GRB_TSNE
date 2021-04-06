'''Most of this should be covered in the notebook'''

import pandas as pd
import os
from astropy.utils.data import download_file
import shutil


def get_summary_files():
    """
    Downloads the required summary files from Swift:
    https://swift.gsfc.nasa.gov/results/batgrbcat/index_tables.html
    and puts them in a folder called summary_files
    """
    urls = {'Duration': 'https://swift.gsfc.nasa.gov/results/batgrbcat/summary_cflux/summary_general_info/summary_burst_durations.txt',
            'Best_fit': 'https://swift.gsfc.nasa.gov/results/batgrbcat/summary_cflux/summary_T100/best_model.txt',
            'PL_fluence': 'https://swift.gsfc.nasa.gov/results/batgrbcat/summary_cflux/summary_T100/summary_pow_energy_fluence.txt',
            'CPL_fluence': 'https://swift.gsfc.nasa.gov/results/batgrbcat/summary_cflux/summary_T100/summary_cutpow_energy_fluence.txt'
            }
    if 'summary' not in os.listdir():
        os.mkdir("summary")
    for sum, url in zip(urls.keys(), urls.values()):
        tmp_path = download_file(url)
        file_path = "summary/{}.dat".format(sum)
        shutil.move(tmp_path, file_path)


def duration_data_to_df():
    """
    This function makes strips the duration data to only contain the required information and puts it in "DataFrames"
    """
    # Create directory
    if 'DataFrames' not in os.listdir():
        os.mkdir("DataFrames")

    # Load and clean DataFrame:
    DF = pd.read_table("summary/Duration.dat", sep="|",
                       comment='#', header=None)  # Load DataFrame
    # print(DF.head())
    DF = DF.loc[:, [0, 1, 3, 4, 5, 6]]  # Only take required columns
    DF.columns = ["GRBname", 'Trig_id', 'T90_start',
                  'T90_end', 'T100_start', 'T100_end']  # Name columns
    # Convert columns to numeric values
    for col in ['T90_start', 'T90_end', 'T100_start', 'T100_end']:
        # If not possible write Nan
        DF[col] = pd.to_numeric(DF[col], errors='coerce')
    DF['T90'] = DF.T90_end - DF.T90_start  # Calculate the T90
    DF.drop_duplicates(subset='GRBname', inplace=True)  # Drop duplicate data
    DF.set_index('GRBname', inplace=True, drop=True)  # Set index to GRBname
    DF.index = DF.index.str.strip()  # Strip GRBname for spaces etc.

    # Save data
    DF.to_pickle("DataFrames/duration_data.dat")

    return None


def fluence_data_to_df():
    """
    Save the best_fit fluence from each GRB and saves it in DataFrames as a pandas DataFrame
    """
    # Load relevant summary files as dataframes
    best_fit = pd.read_table(
        "summary/Best_fit.dat", comment='#', sep='|', header=None, skipinitialspace=True)
    PL_fluence = pd.read_table(
        "summary/PL_fluence.dat", comment='#', sep='|', header=None, skipinitialspace=True)
    CPL_fluence = pd.read_table(
        "summary/CPL_fluence.dat", comment='#', sep='|', header=None, skipinitialspace=True)

    # Set same index: GRBname
    for df in [best_fit, PL_fluence, CPL_fluence]:
        df.set_index(0, drop=True, inplace=True)
        # df.drop_duplicates(subset = 'GRBname', inplace = True) # Drop duplicate data
        # DF.set_index('GRBname', inplace = True, drop = True) # Set index to GRBname
        df.index = df.index.str.strip()  # Strip GRBname for spaces etc.

    # Strip to only total fluence
    PL_fluence = PL_fluence.iloc[:, 20]
    CPL_fluence = CPL_fluence.iloc[:, 20]

    # Replace PL - fluence with CPL if it is a better fit
    CPL_better = best_fit.loc[:, 2].apply(
        lambda x: True if x == 'CPL' else False)
    fluence = PL_fluence[best_fit.index]
    fluence[CPL_better] = CPL_fluence[CPL_better]

    # Save file
    if 'DataFrames' not in os.listdir():
        os.mkdir("DataFrames")
    fluence.to_pickle("DataFrames/fluence_data.dat")


def get_LC(name, trig_id):
    """
    Function to download a lightcurve given it's name and trig_id
    """
    # Find URL
    if len(trig_id) == 6:
        lc_url = "https://swift.gsfc.nasa.gov/results/batgrbcat/%s/data_product/00%s000-results/lc/64ms_lc_ascii.dat" % (
            name, trig_id)
    elif len(trig_id) == 11:
        lc_url = "https://swift.gsfc.nasa.gov/results/batgrbcat/%s/data_product/%s-results/lc/64ms_lc_ascii.dat" % (
            name, trig_id)
    else:
        print('Download %s manually (trig_id to url)' % (name))
        return False

    try:
        tmp_path = download_file(lc_url)
        batlc_path = "LightCurves/%s_lc.dat" % (name)
        shutil.move(tmp_path, batlc_path)
    except:
        print(f"Download {name} manually (not automatically downloaded)")
        return False
    return True


def update_LCs():
    """ Function that downloads the availible light curves. This function will take the duration_data.dat to get list of 
    trig_ids and GRBnames. """

    # Make sure the required files are downloaded
    if 'Duration.dat' not in os.listdir('summary'):
        get_summary_files()
    if 'duration_data.dat' not in os.listdir('DataFrames'):
        duration_data_to_df()
    if 'LightCurves' not in os.listdir():
        os.mkdir("LightCurves")

    # Load trig_ids and names from file
    trig_ids = list(pd.read_pickle(
        "DataFrames/duration_data.dat").loc[:, 'Trig_id'].str.strip())
    names = list(pd.read_pickle("DataFrames/duration_data.dat").index)

    # Already downloaded files
    downloaded = list(map(lambda s: s[: -7], os.listdir("LightCurves")))
    # print(downloaded)

    operations = {'Downloaded': [], 'Error': [], 'Existed': []}
    error_log = ""

    # Loop through names
    for name, trig_id in zip(names, trig_ids):
        if name not in downloaded:  # If not downloaded call function to download
            success = get_LC(name, trig_id)
        else:
            # print(f"{name} is already downloaded")
            operations['Existed'].append(name)
            continue

        # Add to log depending on success of it
        if success:
            # print(f"{name} downloaded successfully ")
            operations['Downloaded'].append(name)
        else:
            print(f"{name} not downloaded")
            operations['Error'].append(name)
            error_log += f"{name} \t downloading error \n"

    # Write errors to log
    err_file = open("Error_log.txt", "w")
    err_file.write(error_log)
    err_file.close()

    # List of operations
    return operations

    # downloaded = map(lambda s: s[: -7], os.listdir("LightCurves"))  # Ret lige i den her
    #

if __name__ == "__main__":  # Make folders if not already in:
    if "summary" not in os.listdir():
        os.mkdir("summary")
    if "DataFrames" not in os.listdir():
        os.mkdir("DataFrames")

    # Update the lightcurves
    fluence_data_to_df()
    log = update_LCs()

