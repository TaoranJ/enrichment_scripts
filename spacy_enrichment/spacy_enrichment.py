# -*- coding: utf-8 -*-

"""

This module implements SpacyEnrichment, which uses `spaCy <https://spacy.io/>`_
package to extract NLP structures from documents. Note that the standard
pipeline of spaCy 2.x is running 10X slower. So if speed really matters, then
use spaCy 1.x.

Functionalities supported are listes as follow:

    1. Tokenization and lemmatization.
    2. Dependency strucutre.
    3. Svos.
    4. Named entities.
    5. Noun chunks.

"""

import json
from collections import defaultdict
import os

import textacy
import spacy

from .base_enricher import BaseEnricher


class SpacyEnrichment(BaseEnricher):
    """Class implementing spacy enrichment.

    Attributes
    ----------
    spy_nlp : spacy.lang.en.English
        spaCy language model.

    """

    if spacy.__version__ == '1.9.0':  # much faster
        spy_nlp = textacy.load_spacy('en_core_web_md')
    else:
        spy_nlp = textacy.load_spacy('en_core_web_lg')

    @classmethod
    def enrich_documents(cls, ipath, args):
        """Enrich records in a raw data file.

        NLP structures are extracted, namely, named entities, noun chunks and
        subject-verb-objects. Tokens and associated meta info are also
        attached.

        Parameters
        ----------
        ipath : str
            /path/to/raw/data/file.

        """

        cfields, opath = args.fields, args.output
        for record_chunk in cls.get_record_chunk(ipath, args.chunk_size):
            records = textacy.corpus.Corpus(cls.spy_nlp)
            text_stream, metadata_stream = cls.split_records(
                    record_chunk, cfields)
            records.add_texts(text_stream, metadata_stream, n_threads=10)
            opath_json = os.path.join(opath,
                                      os.path.basename(ipath) + '.enrich')
            with open(opath_json, 'a') as ofp:
                for record in records:
                    metadata = record.metadata
                    metadata['spacy_enrichment'] = {
                            'token': cls.get_tokens(record)}
                    if args.noun_chunk:
                        metadata['noun_chunks'] = cls.get_noun_chunks(record)
                    if args.svo:
                        metadata['svos'] = cls.get_svos(record)
                    if args.entity:
                        metadata['named_entities'] = \
                                cls.get_named_entities(record)
                    json.dump(metadata, ofp)
                    ofp.write('\n')

    @classmethod
    def get_tokens(cls, doc):
        """Get tokens and associated metadata in a record.

        Each ``token`` entry consists of ``text``, ``lemma``, ``pos``,
        ``head``, ``dep``. Stopwords are removed. Tokens whose POS tag is in
        exclude_pos are removed. Punctuations are removed.

        Parameters
        ----------
        doc : :obj: `textacy.doc.Doc`
            patent handled by textacy Doc.

        Returns
        -------
        list
            a list of noun chunks in records.

        """

        return [{'head': token.head.i, 'index': token.i, 'text': token.text,
                 'lemma': token.lemma_, 'pos': token.pos_, 'dep': token.dep_}
                for token in textacy.extract.words(doc)]

    @classmethod
    def get_noun_chunks(cls, doc):
        """Get noun chunks in a record.

        Determiners of noun chunks are dropped. Noun chunks which contains only
        one word are dropped. Noun chunks are replaced with its lemma form.

        Parameters
        ----------
        doc : :obj: `textacy.doc.Doc`
            patent handled by textacy Doc.

        Returns
        -------
        list
            a list of noun chunks in records.

        """

        noun_chunks = set([nc.lemma_
                           for nc in textacy.extract.noun_chunks(doc)
                           if len(nc) > 1])
        return list(noun_chunks)

    @classmethod
    def get_svos(cls, doc):
        """Get SVOs in a record.

        If S is a single word, then it must be a NOUN. If V is a single word,
        then it must be a VERB. If O is a single word, then it must be NOUN.
        Also, all the words are replaced with their lemmas.

        Parameters
        ----------
        doc : :obj: `textacy.doc.Doc`
            patent handled by textacy Doc.

        Returns
        -------
        list
            a list of triples: (subject, verb, object).

        """

        svos = set()
        for svo in textacy.extract.subject_verb_object_triples(doc):
            if len(svo[0]) == 1 and svo[0].root.pos_ != 'NOUN':
                continue
            if len(svo[1]) == 1 and svo[1].root.pos_ != 'VERB':
                continue
            if len(svo[2]) == 1 and svo[2].root.pos_ != 'NOUN':
                continue
            svos.add((svo[0].lemma_, svo[1].lemma_, svo[2].lemma_))
        return [list(svo) for svo in svos]

    @classmethod
    def get_named_entities(cls, doc):
        """Get named entities in a patent.

        Lemma format of extraced named entities are returned.

        Parameters
        ----------
        doc : :obj: `textacy.doc.Doc`
            patent handled by textacy Doc.

        Returns
        -------
        dict
            a dict mapping named entity to its type like {net : [types]}. Note
            one named entity may have more than one type.

        """
        ents = defaultdict(list)
        for ent in textacy.extract.named_entities(doc):
            ents[ent.lemma_].append(ent.label_)
        ents = {ent: list(set(ents[ent])) for ent in ents}
        return ents
