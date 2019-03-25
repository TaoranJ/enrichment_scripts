# -*- coding: utf-8 -*-

"""

This module implements SpacyEnrichment, which uses `spaCy <https://spacy.io/>`_
package to extract NLP structures from documents.

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

from .utils import get_record_chunk, split_records


def enrich_documents(ipath, args):
    """Enrich records in a raw data file.

    NLP structures are extracted, namely, named entities, noun chunks and
    subject-verb-objects. Tokens and associated meta info are also
    attached.

    Parameters
    ----------
    ipath : str
        /path/to/raw/data/file.

    """

    if args.entity:
        nlp = textacy.load_spacy('en_core_web_lg', disable=('textcat'))
    elif args.noun_chunk or args.svo or args.sents:
        nlp = textacy.load_spacy('en_core_web_lg', disable=('ner', 'textcat'))
    else:
        nlp = textacy.load_spacy('en_core_web_lg',
                                 disable=('parser', 'ner', 'textcat'))
    cfields, opath = args.fields, args.output
    for record_chunk in get_record_chunk(ipath, args.chunk_size):
        records = textacy.corpus.Corpus(nlp)
        text_stream, metadata_stream = split_records(
                record_chunk, cfields)
        records.add_texts(text_stream, metadata_stream, n_threads=10)
        opath_json = os.path.join(opath,
                                  os.path.basename(ipath) + '.enrich')
        with open(opath_json, 'a') as ofp:
            for record in records:
                metadata = record.metadata
                metadata['spacy_enrichment'] = {
                        'token': get_tokens(record)}
                if args.noun_chunk:
                    metadata['noun_chunks'] = get_noun_chunks(record)
                if args.svo:
                    metadata['svos'] = get_svos(record)
                if args.entity:
                    metadata['named_entities'] = \
                            get_named_entities(record)
                if args.sents:
                    metadata['sents'] = [s.lemma_.replace('-PRON-', '')
                                         for s in record.sents]
                json.dump(metadata, ofp)
                ofp.write('\n')


def get_tokens(doc):
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


def get_noun_chunks(doc):
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


def get_svos(doc):
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


def get_named_entities(doc):
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
