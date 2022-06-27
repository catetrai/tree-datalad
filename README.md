# tree-datalad

[![tests](https://github.com/catetrai/tree-datalad/actions/workflows/tests.yml/badge.svg)](https://github.com/catetrai/tree-datalad/actions/workflows/tests.yml)

The `tree` command with added markers for [DataLad](https://github.com/datalad/datalad) dataset.

Helps visualize hierarchies of nested datasets.

## Usage

Options are passed to `tree`:

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

## Requirements

- bash (Linux or macOS)
- tree >= v1.6.0-1
- datalad

## Installation

Copy the shell script [tree-datalad](tree-datalad) to a directory in your `$PATH`, such as `$HOME/bin` or `/usr/local/bin`.
