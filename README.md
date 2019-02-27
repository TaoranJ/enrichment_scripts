# Enrichment Scripts

## Installation

If pip is used, then install requirements with the following command. 

```bash
pip install -r requirements.txt
```
If conda is used, then install create virtual environment and install requirements with the following command.

```bash
conda create --name <env> --file requirements.txt
```

Then download Spacy models. Following command download `en_core_web_lg` for English context enrichment.

```bash
python -m spacy download en_core_web_lg
```

## How to use

```bash
python document_enrichment.py --fields title abstract --inputs ./sample_dataset/patent.sample.json --output .
```

Usage of the script is straightforward. Each line of the input files is in JSON format, in which the context fields are given by `--fields` option.

```json
{
    "id": "3930271", 
    "date": "1976-01-06", 
    "abstract": " A golf glove is disclosed having an extra finger pocket between the index and middle finger pockets for securing one finger of one hand of a golf player between the fingers of the player's other hand. ",
    "title": "Golf glove"
}
```
`--inputs` are the path to input documents. `--ouput` is the ouptut directory.
