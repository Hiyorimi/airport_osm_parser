# Airports OSM Parser

Simple OSM entity parser heavily based on [Pyosmium documentation](https://docs.osmcode.org/pyosmium/latest/intro.html). It extracts all the `aeroway=aerodrome` nodes and geometries and outputs into the .txt files as sequence of coordinates.

## Installation

The obbious prerequsite is [osmium](https://osmcode.org/osmium-tool/), which (on Mac with [brew](https://brew.sh)) can be installed with:

```bash
brew install osmium-tool
```

If you expirience any problems running this script, you can building pyosmium from source:

```bash
pip3 install  osmium --no-binary :all:
```

## Usage

Script supports parsing *.pbf and *.gz compressed OSM files.

```bash
$ ./airports_parser.py
usage: airports_parser.py [-h] [-v] -i INPUT_FILE -o OUTPUT_ID
airports_parser.py: error: the following arguments are required: -i/--input-file, -o/--output-id
```