# tree-datalad

[![tests](https://github.com/catetrai/tree-datalad/actions/workflows/tests.yml/badge.svg)](https://github.com/catetrai/tree-datalad/actions/workflows/tests.yml)

The `tree` command with added markers for [DataLad](https://github.com/datalad/datalad) datasets. Helps visualize hierarchies of nested datasets.

## Usage

`tree-datalad` works just like `tree`. You can pass it any `tree` options.

### Examples

View a hierarchy of nested subdatasets in the context of the whole directory layout:

```
❯ tree-datalad -d -L 3 bids
bids  <--[DS]
├── code
│   └── common
├── data
│   ├── inputs
│   │   └── dicom  <--[DS]
│   └── outputs
│       ├── sub-01
│       └── sub-02
└── environments  <--[DS]
    ├── images
```

Find datasets at all depths of the current directory tree:

```
❯ tree-datalad -d -f | grep '\[DS\]'
├── ./bids  <--[DS]
│   │   │   └── ./bids/data/inputs/dicom  <--[DS]
│   ├── ./bids/environments  <--[DS]
└── ./dicom  <--[DS]
```

## Requirements

- bash (Linux or macOS)
- tree >= v1.6.0-1
- datalad

## Installation

Copy the shell script [tree-datalad](tree-datalad) to a directory in your `$PATH`, such as `$HOME/bin` or `/usr/local/bin`.
