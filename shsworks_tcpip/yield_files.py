
import os
from pathlib import Path


def yield_all_files(path, suffix):
    """ generator for absolute path of all filenames in path ending with extention given by suffix.

    Args:
        suffix (str): e.g. ".csv", ".shz" etc.

    Yields:
        pathlib.Path

    Example:
        >>> for fname in yield_all_files(path, '.shz'):
        >>>     print(fname)
        >>>     # do stuff with fname
    """
    for fname in os.listdir(path):
        sub_path = Path(path, fname)
        if sub_path.is_file() and (sub_path.suffix == suffix):
            yield sub_path


def yield_all_shzs(path):
    """Generator for all shz files in the path.

    Example:
        >>> from pathlib import Path
        >>>
        >>> with Client() as c:
        >>>     path = Path(r'C:/path/to/your/measurements')
        >>>     for shz_path in yield_all_shzs(path):
        >>>         print(fname)
        >>>         c.load_file()
        >>>         c.evaluation()
    """
    for shz_path in yield_all_files(path, '.shz'):
        yield shz_path

def get_shz_files(path) -> list:
    """Returns list of all SHZ files in the directory

    Args:
        path (Path): folder containing the shz files

    Returns:
        list: contains instances of Path.

    Raises:
        FileNotFoundError: if there are no SHZ files in the directory.
    """
    file_list = [p for p in yield_all_shzs(path)]
    if len(file_list) == 0:
        raise FileNotFoundError(f'There are no SHZ files in {path}')
    return file_list
