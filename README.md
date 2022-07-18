# woff2otf

This is a small utility to convert WOFF files to the OTF font format. It uses Python 3, so you need to have it installed in order to run it.

## Usage
To run the script, simply invoke it from the command line:
```
./woff2otf.py font.woff|src-directory [font.otf|dst-directory]
```

The first parameter is the source file (the WOFF) font or a directory containing (other directories with) WOFF files, and the second parameter is the output file (in OTF format) or a directory which will contain the OTF files. When using directories, the subdirectories structure will be kept.
