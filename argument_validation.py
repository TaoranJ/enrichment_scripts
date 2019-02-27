# -*- coding: utf-8 -*-

"""

Common parameter validation for argparser.

"""

import os


def files_path_validation(paths):
    """ Validation of a list of file paths.

    Parameters
    ----------
    paths : list
        A list of paths to files.

    Raises
    ------
    FileNotFoundError
        Raised if ``path`` doesn't exist.

    """

    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError('File {0} is not there.'.format(path))


def file_path_validation(path):
    """File path validation.

    Parameters
    ----------
    path : str
        /path/to/a/file.

    Raises
    ------
    FileNotFoundError
        Raised if ``path`` doesn't exist.

    """

    if not os.path.exists(path):
        raise FileNotFoundError('File {0} is not there.'.format(path))


def dir_path_validation(path, create_dir=False):
    """Directory path validation.

    Parameters
    ----------
    path : str
        /path/to/a/directory/.
    create_dir : bool
        If True, a new directory will be made once it doesn't exist.

    Raises
    ------
    FileNotFoundError
        Raised if ``path`` doesn't exist.
    NotADirectoryError
        Raised if ``path`` is not a directory.

    """

    if not os.path.exists(path):
        if create_dir:
            os.makedirs(path)
        else:
            raise FileNotFoundError('Directory {0} is not there.'.format(path))
    elif not os.path.isdir(path):
        raise NotADirectoryError('{0} is not a directory.'.format(path))
