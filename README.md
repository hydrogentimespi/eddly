# eddly

## Introduction

Eddly is a python-based parsing library for the electronic device description language (edd).
The edd describes how to configure and communicate with a field device.
It is standardized with IEC 61804. Find more details at https://en.wikipedia.org/wiki/Device_Description_Language

This library can read a *.ddl file and generate a python data structure from it.
This may be used for generating documentation (menu trees, command lists,...) or writing a communication tool for a field device.
It uses the python-based parsing framework SLY (thanks to David Beazley) and the C99 preprocessor pcpp (thanks to Niall Douglas and David Beazley).
It requires the use of Python 3.6 or greater.

## License

This work is distributed under the MIT license. See [LICENSE](LICENSE) for details.

## Features

- supports C-like preprocessing (#include, #define,...) with preprocessed output for debugging
- can read standard dc8 text libraries and handle [text_ref] references
- basic parsing support for COMMANDs, VARIABLEs, MENUs with focus on HART. Other edd keywords (IMPORT, METHOD, GRID, IF, ELSE,...) currently unsupported.
- print menu tree in ascii-art.

## How it works

A main *.ddl file is provided as input.
 - Step 1: file is given to the preprocessor pcpp (#include files, remove /* comments */, replace #define macros,...)
 - Step 2: preprocessed output is passed to SLY's lexer (identify tokens like 'COMMAND', 'LABEL', numbers, strings,...)
 - Step 3: lexed tokens are parsed by SLY's parser
 - Step 4: dicts for commands, variables, menues are generated for further processing.

The demo.py file will print
```python
# Edd meta data: manufacturer 255, device type 38911, dd revision 1, device revision 1
# commands
{   'write_configuration': {   'NUMBER': 555,
                               'OPERATION': 'WRITE',
                               'TRANSACTIONS': {   0: {   'REQUEST': [   'config_data']}}}}
# variables
{   'sensor_unit': {   'CLASS': ['LOCAL', 'DYNAMIC'],
                       'FORMAT': 'UNSIGNED_INTEGER',
                       'HANDLING': ['READ', 'WRITE'],
                       'SIZE': 1},
    'sensor_value': {   'CLASS': ['LOCAL', 'DYNAMIC'],
                        'FORMAT': 'FLOAT',
                        'HANDLING': ['READ', 'WRITE'],
                        'LABEL': 'Measurement'}}
# menues
{   'configuration_menu': {   'ITEMS': ['sensor_value', 'sensor_unit'],
                              'LABEL': 'Configuration menu'},
    'diagnostics_menu': {   'ITEMS': ['"device status"', '"process status"'],
                            'LABEL': 'Diagnostics menu'},
    'root_menu': {   'ITEMS': ['configuration_menu', 'diagnostics_menu'],
                     'LABEL': 'Main menu'}}
   Main menu
   ├─── Configuration menu
   │    ├─── Measurement
   │    └─── sensor_unit
   └─── Diagnostics menu
        ├─── device status
        └─── process status
```

## Installation

Install required external modules with
```sh
pip install sly pcpp
```

## TODO

- improve handling and ignoring of unsupported keywords; get rid of sly WARNING messages. Parsing currently fails if ignored keyword is the last in pp'ed input

## Caution

This is a hobby project and a proof-of-concept. Only a fraction of the edd language is implemented.
It is far away from implementing the whole IEC 61804, so it is not standard conformant. What is implemented may be wrong.  
Use it on your own risk!

## Contribution

Welcome. Thanks to all contributors.

