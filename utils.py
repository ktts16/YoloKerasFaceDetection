from pathlib import Path
import pandas as pd
import os
import re
import numpy as np

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


def scale_and_recenter_points(points, old_size, new_size):
    debug = False
    # debug = True

    points3d = np.transpose(points)

    (h, w) = old_size
    (cX, cY) = (w // 2, h // 2)
    (nH, nW) = new_size
    (scaleH, scaleW) = (nH/h, nW/w)

    # compute the new bounding dimensions of the image
    points3d_n = points3d.copy()

    # adjust the rotation matrix to take into account translation
    points3d_n[0,:] *= scaleW
    points3d_n[1,:] *= scaleH

    points3d_n[0,:] += (nW / 2)## - cX
    points3d_n[1,:] += (nH / 2)## - cY

    if debug:
        print('points3d', points3d)
        print('scaleH; scaleW', scaleH, scaleW)
        print('nW; nH', nW, nH)

    # perform the actual rotation and return the image
    return np.transpose(points3d_n)
