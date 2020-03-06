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

    (h, w) = old_size
    (cX, cY) = (w // 2, h // 2)
    (nH, nW) = new_size
    (scaleH, scaleW) = (nH/h, nW/w)

    # compute the new bounding dimensions of the image
    points3d_n = points.copy()

    # adjust the rotation matrix to take into account translation
    points3d_n[:,0] *= scaleW
    points3d_n[:,1] *= scaleH

    points3d_n[:,0] += (nW / 2)## - cX
    points3d_n[:,1] += (nH / 2)## - cY

    if debug:
        print('points3d', points3d)
        print('scaleH; scaleW', scaleH, scaleW)
        print('nW; nH', nW, nH)

    # perform the actual rotation and return the image
    return points3d_n


def all_equal(arr, value):
    if isinstance(arr, list):
        arr = np.array(arr)
    return np.all(arr == value, axis = 0)


def ndarray_to_list(arr):
    ls = None
    if isinstance(arr[0], np.ndarray) and all_equal([el.shape[0] for el in arr], 1):
        ls = [el[0] for el in arr]
    elif isinstance(arr[0], np.uint16) or isinstance(arr[0], np.float64):
        ls = arr
    return ls


def str_to_int(string):
    var = None
    if string.isdigit():
        var = int(string)
    return var


from math import isclose, isnan

def is_equal_to_df_column(arr, df_column):
    if not (isinstance(arr, np.ndarray) or isinstance(arr, list)):
        raise Exception("'df_column' is not of type 'numpy.ndarray' or 'list'.")
    if not isinstance(df_column, pd.core.series.Series):
        raise Exception("'df_column' is not of type 'pandas.core.series.Series'.")
    if len(arr) != df_column.shape[0]:
        print('#rows:', len(arr), df_column.shape[0], df_column.shape)
        raise Exception('Failed: # rows are not equal')
    else:
        print('Passed: # rows are equal', len(arr), df_column.shape[0], sep='\t')
    is_equal = []
    for idx in range(len(arr)):
        if isinstance(arr[idx], np.float64):
            if isnan(arr[idx]) and isnan(df_column.iloc[idx]):
                v = True
            else:
                v = isclose(arr[idx], df_column.iloc[idx], rel_tol=1e-6)
        else:
            v = arr[idx] == df_column.iloc[idx]
        is_equal.append(v)
    index_not_equal = [i for i, eq in enumerate(is_equal) if eq == False]
    return all_equal(is_equal, True), is_equal, index_not_equal


from PIL import Image
from itertools import combinations

# Source: https://stackoverflow.com/questions/51688179/check-if-there-is-exactly-the-same-image-as-input-image

def compare_images(input_image, output_image, give_reason=False):
    # compare image dimensions (assumption 1)
    if input_image.size != output_image.size:
        if give_reason:
            return (False, 'image sizes are different.') if give_reason else False

    rows, cols = input_image.size

    # compare image pixels (assumption 2 and 3)
    for row in range(rows):
        for col in range(cols):
            input_pixel = input_image.getpixel((row, col))
            output_pixel = output_image.getpixel((row, col))
            if input_pixel != output_pixel:
                return (False, 'pixel values and/or orientation are different.') if give_reason else False

    return (True, None) if give_reason else True


def all_images_duplicate(image_files):
    ans = (None, None)
    if len(image_files) >= 2:
        index_pairs = [comb for comb in combinations(range(len(image_files)), 2)]
        is_duplicate = []
        for pair in index_pairs:
            input_img = image_files[pair[0]]
            output_img = image_files[pair[1]]
            is_duplicate.append(compare_images(Image.open(input_img), Image.open(output_img)))
        ans = (all(is_duplicate), is_duplicate)
    return ans


def list_files(path, ext="", rel_path=True):
    filelist = []
    for root, dirs, files in os.walk(path):
        for name in files:
            name = name.replace("."+ext, "") if len(ext) else name
            filelist.append((
                root.replace(path+"/", ""),
                name
                ) if rel_path else name)
    return filelist


def find_file_with_name_len(filelist, name, ext):
    file = None
    matches = [(subdir, fname) for subdir, fname in filelist if len(fname) == len(name) and name == fname]
    if len(matches) == 1:
        subdir, fname = matches[0]
        file = os.path.join(subdir, fname + "." + ext)
    return file


def find_file_in(filelist, name, ext):
    for file in filelist:
        if "/" + name + "." + ext in file:
            return file
    return None


def prepare_dst_directory(path, subsets=["train", "validation"], classes=["f", "m"]):
    if not os.path.exists(path):
        os.makedirs(path)

    for s in subsets:
        for c in classes:
            p = os.path.join(path, s, c)
            if not os.path.exists(p):
                os.makedirs(p)


def find_path_of_files(image_group, filelist, ext, path, verbose=False):
    # find files with rm id (IMDB id)
    files = []
    for idx, _ in image_group:
        filename = str(idx)
        file = find_file_with_name_len(filelist, filename, ext)
        if verbose:    print(idx, file)
        if file is None:
            if verbose:    print('NOT EXIST:', filename)
        else:
            files.append(os.path.join(path, file))
    return files


from shutil import move

def move_files(files, from_path, to_path, verbose=False):
    for file in files:
        subdir = file.replace(from_path + ("" if from_path[-1] == "/" else "/"), "")
        move(file, os.path.join(to_path, subdir))
        if verbose:
            print('move:', file, '\t to:', subdir)
