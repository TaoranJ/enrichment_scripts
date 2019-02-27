# Enrichment Scripts

## Installation

```bash
# if pip is used
pip install -r requirements.txt
# if conda is used
conda create --name <env> --file requirements.txt
# download Spacy corpus (e.g., en_core_web_lg)
python -m spacy download en_core_web_lg
```

## How to use

```bash
python document_enrichment.py --fields title abstract --inputs ./sample_dataset/patent.sample.json --output .
```

Usage of the script is straightforward. Each line of the input files is in JSON format, in which the context fields are given by `--fields` option.

```json
{"id": "3930271", "type": "utility", "number": "3930271", "country": "US", "date": "1976-01-06", "abstract": " A golf glove is disclosed having an extra finger pocket between the index and middle finger pockets for securing one finger of one hand of a golf player between the fingers of the player's other hand. ", "title": "Golf glove", "kind": "A", "num_claims": "4", "filename": "pftaps19760106_wk01.zip"}
```
`--inputs` are the path to input documents. `--ouput` is the ouptut directory.
