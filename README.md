# jinr-database-tools
Tools for load data to database

* Create json description for data file
* Validate json (json specification see in HTML documentation)
* Load data to database

## Installation

Dev installation: `pip install -e .`

## Usage

### GUI

Run: `smart-data-parser-gui` or `python main_gui.py`

### CLI

Run `smart-data-parser` or `python main_cli.py`

For example: 
`smart-data-parser load -c config.json -d tests/data/detector_.json tests/data/detector_.csv`

Run: `smart-data-parser -h` for this help:
```
usage: smart-data-parser [-h] command ...

Parse input data file and load to database

positional arguments:
  command
    validate  Validate JSON file with input data format
    load      Parse input data file and load to database
    format    Open description of the JSON schema for input data
    generate  Generate JSON templates from database

optional arguments:
  -h, --help  show this help message and exit
```
For getting help by command run: `smart-data-parser command -h`.