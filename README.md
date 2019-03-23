# Enrichment Scripts

Simple and easy-to-use scripts for enrichment on text content. Multiprocessing is supported. 

## Requirement

If `pip` is used: 
```bash
pip install textacy
```

If `conda` is used:
```bash
conda install -c conda-forge textacy
```

Then download Spacy models. Following command download `en_core_web_lg` for English context enrichment.

```bash
python -m spacy download en_core_web_lg
```

## How to use

Usage of the script is straightforward. Each line of the input files is in JSON format, in which the context fields are given by `--fields` option.

For example, given **each line of the input file** has the format below.
```json
{
    "id": "3930271", 
    "date": "1976-01-06", 
    "abstract": " A golf glove is disclosed having an extra finger pocket between the index and middle finger pockets for securing one finger of one hand of a golf player between the fingers of the player's other hand. ",
    "title": "Golf glove"
}
```

Enrichment can be done by running comand below.
```bash
python document_enrichment.py --cores 2 --fields title abstract --inputs ./sample_dataset/patent.sample.* --output .
```
where `--inputs` is the path to input documents. `--ouput` is the ouptut directory. `--cores` tells script how many cores to use.
