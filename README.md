# woff2otf

This is a small utility to convert WOFF files to the OTF font format. It uses Python 3, so you need to have it installed in order to run it.

## Usage
To run the script, simply invoke it from the command line:
```
./woff2otf.py font.woff font.otf
```

The first parameter is the source file (the WOFF) font, and the second parameter is the output file (in OTF format).

### Note to OS X users
The utility looks for `python3` in `/usr/bin/`. If you have it installed in `/usr/local/bin/` (use the command `which python3` to check), just replace `/usr/bin` with `/usr/local/bin` in the first line of the file.
