# jinr-database-tools
Tools for load data to database

* Create json description for data file
* Validate json (json specification see in HTML documentation)
* Load data to database

## Installation

Dev installation: `pip install -e .`

## Usage

### GUI

Run: `jinr-database-loader-gui`

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

Исправления по GUI
Исправлено 1, 2, 6, 7

Исправления по CLI:
Исправлены: 1, 3, 4, 5, 6, 8, 11, 13

2 "positional arguments:" -> "commands" это зашито в парсер аргументов, так просто исправить не получится.

7 Сделал обработку ошибки, если конфиг не сущетсвует.

10 Добавил файл в корень проекта, добавил обработку различных ошибок

12 Заменил на вывод конкретного ответа от database API

Ошибка с подключение к базе данных связана с потерей совместимости между SqlAlchemy 1.3 и 1.4. 
Сейчас я сделал поддержку обоих версий, но надо решить что мы делаем: прибиваем гвоздями версию sqlalchemy (и заодно других библиотек) в setup.py (но тогда если другим приложения нужна будет другая версия, то их придется разносить по разным виртуальным окружениям) --- так обычно делают на веб-сервисах, либо надо будет отслеживать возможную потерю совместимости при обновлении библиотек.
