from pathlib import Path

def get_local_dataset_root_path(suffix='/'):
    return str(Path.home()) + suffix