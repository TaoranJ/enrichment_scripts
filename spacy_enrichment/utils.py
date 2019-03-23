# -*- coding: utf-8 -*-

"""Base class for spacy-based enrichers."""

import json
from itertools import chain, islice, tee, starmap
from cytoolz import itertoolz


def get_record(ipath):
    """Generate one record each time.

    Parameters
    ----------
    ipath : str
        /path/to/records/file.

    Yields
    ------
    dict
        Record in dict format.

    """

    with open(ipath, 'r') as ifp:
        for record in ifp:
            try:
                record = json.loads(record)
                if not isinstance(record, dict):  # not a dict
                    continue
                yield record
            except ValueError:  # bad format
                continue


def get_record_chunk(ipath, size):
    """Generator a record chunk each time.

    Parameters
    ----------
    ipath : str
        /path/to/records/file.

    Yields
    ------
    dict
        Record in dict format.

    """

    iterator = iter(get_record(ipath))
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))


def split_records(records, cfields):
    """

    Generate two streams from records, namely, content stream and metadata
    steam.

    """

    return unzip(((
        '\n'.join([record.pop(cfield) for cfield in cfields]), record)
        for record in records))


def unzip(seq):
    """

    Borrowed from ``toolz.sandbox.core.unzip``, but using cytoolz instead
    of toolz to avoid the additional dependency.

    """

    seq = iter(seq)
    # check how many iterators we need
    try:
        first = tuple(next(seq))
    except StopIteration:
        return tuple()  # and create them
    niters = len(first)
    seqs = tee(itertoolz.cons(first, seq), niters)
    return tuple(starmap(itertoolz.pluck, enumerate(seqs)))
