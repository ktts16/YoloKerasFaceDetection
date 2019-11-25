from pathlib import Path
import pandas as pd
import os
import re

def get_local_dataset_root_path(suffix='/'):
    return str(Path.home()) + suffix


def index_of(filenames_series, filename):
    try:
        return filenames_series.str.startswith(filename + ".").tolist().index(True)
    except ValueError:
        raise Exception('File not found in this directory. Please change file name.')


def remove_extension(s):
    sub_ind = [m.start() for m in re.finditer("\.", s)]
    if len(sub_ind):
        return (s[:sub_ind[-1]], sub_ind[-1])
    else:
        return None


def get_sorted_filenames_and_dataframe(filenames):
    filenames_df = pd.DataFrame(filenames)

    # sort according to int image id from filename format: ""%d.jpg"
    sorted_index = filenames_df[0].str.rsplit('.').str[0].astype(int).sort_values().index
    filenames_df = filenames_df.reindex(index=sorted_index)
    filenames_list_sorted = filenames_df[0].tolist()
    start_index_int, str_idx = remove_extension(filenames_df[0][sorted_index[0]])
    return (filenames_list_sorted, filenames_df, start_index_int)
