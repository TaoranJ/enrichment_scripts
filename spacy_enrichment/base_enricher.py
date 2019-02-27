# -*- coding: utf-8 -*-

"""Base class for spacy-based enrichers."""

import json
from itertools import chain, islice, tee, starmap
from cytoolz import itertoolz


class BaseEnricher(object):
    """Common functions for a spacy-based enricher are implemented here.

    """

    @classmethod
    def get_record(cls, ipath):
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

    @classmethod
    def get_record_chunk(cls, ipath, size):
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

        iterator = iter(cls.get_record(ipath))
        for first in iterator:
            yield chain([first], islice(iterator, size - 1))

    @classmethod
    def split_records(cls, records, cfields):
        """

        Generate two streams from records, namely, content stream and metadata
        steam.

        """

        return cls.unzip(((
            '\n'.join([record.pop(cfield) for cfield in cfields]), record)
            for record in records))

    @classmethod
    def unzip(cls, seq):
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
