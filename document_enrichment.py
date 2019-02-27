# -*- coding: utf-8 -*-

"""

The following script performs the necessary NLP enrichment on the documents.

Examples
--------

.. code-block:: bash

   python document_enrichment --patent --inputs \
sample_dataset/patent.sample.json --output .

"""

import os
import argparse
import multiprocessing as mp

from spacy_enrichment.spacy_enrichment import SpacyEnrichment
from spacy_enrichment.predefined import GNIP_CONTENT, PATENT_CONTENT
from spacy_enrichment.predefined import PUBLICATION_CONTENT


def run_enricher(cores, cfields, ipaths, opath, chunk_size=10000,
                 batch_size=1000):
    """

    Perform enrichment on multiple document files in parallel.

    Parameters
    ----------
    cores : int
        # of cores to use.
    cfields : list
        List of fields which have document contents saved.
    ipaths : list
        List of data files to enrich.
    opath : str
        /path/to/output/dir/.
    chunk_size : int
        # of documents to load into memory once.
    batch_size : int
        Buffersize for one batch.

    """

    if cores == 1:
        for ipath in ipaths:
            SpacyEnrichment.enrich_documents(cfields, ipath, opath, chunk_size,
                                             batch_size)
    else:
        pool = mp.Pool(cores)
        for ipath in ipaths:
            res = pool.apply_async(
                    SpacyEnrichment.enrich_documents,
                    args=(cfields, ipath, opath, chunk_size, batch_size, ))
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
    group = pparser.add_mutually_exclusive_group()
    group.add_argument('--patent', action='store_true',
                       help='Use predefiend patent format. See '
                       'spacy_enrichment/predefined.py')
    group.add_argument('--gnip', action='store_true',
                       help='Use predefiend tweet format. See '
                       'spacy_enrichment/predefined.py')
    group.add_argument('--publication', action='store_true',
                       help='Use predefiend publication format. See '
                       'spacy_enrichment/predefined.py')
    group.add_argument('--fields', nargs='+', type=str,
                       help='Content fields to enrich.')
    pparser.add_argument('--cores', type=int, default=1,
                         help='How many cores to use?')
    pparser.add_argument('--inputs', nargs='+', required=True,
                         help='Path to input documents')
    pparser.add_argument('--output', required=True, help='Path to output dir.')
    pparser.add_argument('--chunk_size', type=int, default=128,
                         help='# of documents to handle at once')
    args = pparser.parse_args()
    files_path_validation(args.inputs)
    dir_path_validation(args.output, create_dir=True)
    if args.gnip:
        run_enricher(args.cores, GNIP_CONTENT, args.inputs, args.output,
                     args.chunk_size, 1000)
    elif args.patent:
        run_enricher(args.cores, PATENT_CONTENT, args.inputs, args.output,
                     args.chunk_size, 64)
    elif args.publication:
        run_enricher(args.cores, PUBLICATION_CONTENT, args.inputs, args.output,
                     args.chunk_size, 1000)
    else:
        run_enricher(args.cores, args.fields, args.inputs, args.output,
                     args.chunk_size, 64)
