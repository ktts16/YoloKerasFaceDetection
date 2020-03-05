from os.path import exists
from os import makedirs
import csv

def prepare_csv_path(path=None):
    csv_path = path if path is not None else 'csv'
    if not exists(csv_path):
        makedirs(csv_path)


def create_csv_writer(csv_file):
    return csv.writer(csv_file, delimiter=',')


def overwrite_and_clear_content(csv_filepath, initial_content=None):
    with open(csv_filepath, mode='w') as csv_file:
        writer = create_csv_writer(csv_file)
        if initial_content is not None:
            for row in initial_content:
                writer.writerow(row)
        else:
            writer.writerow([])


def close_file(file, verbose=True):
    if not file.closed:
        print('Closed file:', file)
        file.close()
