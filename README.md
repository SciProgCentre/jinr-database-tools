# jinr-database-tools
Tools for load data to database

* Create json description for data file
* Validate json (json specification see in HTML documentation)
* Load data to database

## Installation

Dev instalation: `pip install -e .`

## Usage

### CLI

For example: 
`jinr-database-loader load -c tests/config.json -d tests/data/detector_.json tests/data/detector_.csv`

Run: `jinr-database-loader -h` for this help:
```
usage: jinr-database-loader [-h] command ...

Add file to database.

positional arguments:
  command
    validate   Validate json file
    load       Load file to database
    json_schema
               Open HTML documentation for JSON Schema
    generate   Generate json templates from database

optional arguments:
  -h, --help   show this help message and exit

```