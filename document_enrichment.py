# -*- coding: utf-8 -*-

"""

The following script performs the necessary NLP enrichment on the documents.

Examples
--------

.. code-block:: bash

   python document_enrichment --cores 2 --fields title abstract --inputs \
sample_dataset/patent.sample* --output .

"""

import os
import argparse
import multiprocessing as mp

from spacy_enrichment.spacy_enrichment import SpacyEnrichment


def run_enricher(args):
    """

    Perform enrichment on multiple document files in parallel.

    Parameters
    ----------
    args : dict
        Arguments.

    """

    if args.cores == 1:
        for ipath in args.inputs:
            SpacyEnrichment.enrich_documents(ipath, args)
    else:
        pool = mp.Pool(args.cores)
        for ipath in args.inputs:
            res = pool.apply_async(
                    SpacyEnrichment.enrich_documents, args=(ipath, args, ))
        pool.close()
        pool.join()
        if not res.successful():
            print(res.get())


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


if __name__ == "__main__":
    pparser = argparse.ArgumentParser()
    pparser.add_argument('--fields', nargs='+', type=str,
                       help='Content fields to enrich.')
    pparser.add_argument('--cores', type=int, default=2,
                         help='How many cores to use?')
    pparser.add_argument('--noun-chunk', action='store_true',
                         help='generate noun chunks')
    pparser.add_argument('--svo', action='store_true',
                         help='generate svo')
    pparser.add_argument('--entity', action='store_true',
                         help='generate entities')
    pparser.add_argument('--inputs', nargs='+', required=True,
                         help='Path to input documents')
    pparser.add_argument('--output', required=True, help='Path to output dir.')
    pparser.add_argument('--chunk-size', type=int, default=128,
                         help='# of documents to handle at once')
    args = pparser.parse_args()
    files_path_validation(args.inputs)
    dir_path_validation(args.output, create_dir=True)
    run_enricher(args)
