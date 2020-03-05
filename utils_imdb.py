from datetime import datetime
import numpy as np

def calc_age(taken, dob):
    birth = datetime.fromordinal(max(int(dob) - 366, 1))
    if birth.month < 7:
        return taken - birth.year
    else:
        return taken - birth.year - 1


def is_valid(face_score,second_face_score,age,gender):
    if face_score < 1.0:
        return False
    if (~np.isnan(second_face_score)) and second_face_score > 0.0:
        return False
    if not(0 <= age <= 100):
        return False
    if np.isnan(gender):
        return False
    return True


# calculate year of birth
# adapted from:    annotation_imdb_keras.py :: calc_age
def yob(dob):
    birth = datetime.fromordinal(max(int(dob) - 366, 1))
    if birth.month < 7:
        return birth.year
    else:
        return birth.year - 1

# Source: moved from imdb_clean_age.ipynb
from scipy import io as spio
from os.path import exists
from utils import get_local_dataset_root_path, all_equal, ndarray_to_list
from pandas import DataFrame

class IMDBDataSet:
    def __init__(self, ):
        if(exists("./dataset/imdb_crop/")):
            DATASET_ROOT_PATH = ""
        else:
            DATASET_ROOT_PATH = get_local_dataset_root_path()
        self.IMDB_PATH = DATASET_ROOT_PATH+"dataset/imdb_crop/"
        # load data
        print('... Loading IMDB metadata. Please wait. ...')
        self.meta = spio.loadmat(self.IMDB_PATH+"imdb.mat")
        if "imdb" in self.meta:
            if self.meta["imdb"].shape == (1,1): 
                self.meta = self.meta["imdb"][0,0]
        print('Finished loading IMDB metadata.')
        self.column_names = ["full_path", "dob", "gender", "photo_taken", "face_score", "second_face_score", "name"]


    def is_column_type_consistent(self, verbose=False):
        outer_types = [isinstance(self.meta[cn], np.ndarray) for cn in self.column_names]
        inner_types = [isinstance(self.meta[cn][0], np.ndarray) for cn in self.column_names]
        element_types = [type(self.meta[cn][0][0]) for cn in self.column_names]

        if verbose:
            print("outer_types :", outer_types, sep='\t')
            print("inner_types :", inner_types, sep='\t')
            print("Consistent outer_types ?", all_equal(outer_types, True), sep='\t')
            print("Consistent inner_types ?", all_equal(inner_types, True), sep='\t')
            print("element_types:")
            for name in self.column_names:
                print('  - ', name, type(self.meta[name][0][0]), sep='\t')

        return all_equal(outer_types, True) and all_equal(inner_types, True)


    def is_column_shape_consistent(self, verbose=False):
        '''
        Check if all columns have same shape and ...
            all rows of the column of type numpy.ndarray have same length (# elements).
        '''
        outer_shapes = [self.meta[cn].shape for cn in self.column_names]
        inner_shapes = [self.meta[cn][0].shape for cn in self.column_names]

        if verbose:
            print("outer_shapes :", outer_shapes, sep='\t')
            print("inner_shapes :", inner_shapes, sep='\t')
            print("Consistent outer_shapes ?", all_equal(outer_shapes, outer_shapes[0]), sep='\t')
            print("Consistent inner_shapes ?", all_equal(inner_shapes, inner_shapes[0]), sep='\t')

        for cn in self.column_names:
            if isinstance(self.meta[cn][0][0], np.ndarray):
                col0 = self.meta[cn][0]
                col0_len_element = [len(element) for element in col0]
                if verbose:
                    print("Consistent element length of column: '%s' ? \t" % (cn), all_equal(col0_len_element, 1))

        return all(list(all_equal(outer_shapes, outer_shapes[0]))) and all_equal(inner_shapes, inner_shapes[0])


    def to_pandas_dataframe(self, verbose=False):
        if verbose:
            print('\n> is_column_type_consistent')
        c1 = self.is_column_type_consistent(verbose)
        if verbose:
            print('\n> is_column_shape_consistent')
        c2 = self.is_column_shape_consistent(verbose)
        if not c1:
            raise Exception('Inconsistent column types')
        if not c2:
            raise Exception('Inconsistent column shapes')
        self.meta_df = None
        if c1 and c2:
            df = DataFrame()
            for cn in self.column_names:
                if isinstance(self.meta[cn][0][0], np.ndarray):
                    df[cn] = [r[0] for r in self.meta[cn][0] if len(r) == 1]
                else:
                    df[cn] = self.meta[cn][0]
            self.meta_df = df


    def calculate_age(self):
        self.meta_df['age'] = [calc_age(photo_taken, dob) for photo_taken, dob in zip(self.meta_df['photo_taken'], self.meta_df['dob'])]


    def is_image_valid(self):
        self.meta_df['is_image_valid'] = [is_valid(fs1, fs2, age, gender)
            for fs1, fs2, age, gender in zip(self.meta_df.face_score, self.meta_df.second_face_score, self.meta_df.age, self.meta_df.gender)]
        self.valid = [index for index, item in self.meta_df['is_image_valid'].iteritems() if item == True]


def IMDB_url(nameID, imageID):
    return 'https://www.imdb.com/name/' + nameID + '/mediaviewer/' + imageID


def serialize_filename(file):
    if '.' not in file:
        return None
    name_no_ext = file
    if '/' in file:
        name_no_ext = name_no_ext.split('/')[-1]
    name_no_ext = name_no_ext.split('.')[0] 
    if name_no_ext.count('_') != 3:
        return None
    nameID, imageID, dob, taken = name_no_ext.split('_')
    return nameID, imageID, dob, taken


def serialize_filenames(files, enumerated=False):
    for idx, file in enumerate(files):
        nameID, imageID, dob, taken = serialize_filename(file)
        if enumerated:
            yield idx, nameID, imageID, dob, taken
        else:
            yield nameID, imageID, dob, taken


def iterate_filter_len(dt, val_len, operator='eql'):
    for key, value in dt.items():
        if operator == 'eql':
            if len(value) == val_len:
                yield key, value
        elif operator == 'gte':
            if len(value) >= val_len:
                yield key, value


def gender_np_float64_to_str(n):
    return 'M' if n == 1.0 else 'F'
