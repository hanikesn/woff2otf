#!/usr/bin/env python3
#
# Copyright 2012, Steffen Hanikel (https://github.com/hanikesn)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# A tool to convert a WOFF back to a TTF/OTF font file, in pure Python

import struct
import sys
import zlib
from pathlib import Path
from typing import Union, BinaryIO


def convert_streams(infile: BinaryIO, outfile: BinaryIO):
    WOFFHeader = {
        "signature": struct.unpack(">I", infile.read(4))[0],
        "flavor": struct.unpack(">I", infile.read(4))[0],
        "length": struct.unpack(">I", infile.read(4))[0],
        "numTables": struct.unpack(">H", infile.read(2))[0],
        "reserved": struct.unpack(">H", infile.read(2))[0],
        "totalSfntSize": struct.unpack(">I", infile.read(4))[0],
        "majorVersion": struct.unpack(">H", infile.read(2))[0],
        "minorVersion": struct.unpack(">H", infile.read(2))[0],
        "metaOffset": struct.unpack(">I", infile.read(4))[0],
        "metaLength": struct.unpack(">I", infile.read(4))[0],
        "metaOrigLength": struct.unpack(">I", infile.read(4))[0],
        "privOffset": struct.unpack(">I", infile.read(4))[0],
        "privLength": struct.unpack(">I", infile.read(4))[0],
    }

    outfile.write(struct.pack(">I", WOFFHeader["flavor"]))
    outfile.write(struct.pack(">H", WOFFHeader["numTables"]))
    maximum = list(
        filter(
            lambda x: x[1] <= WOFFHeader["numTables"], [(n, 2**n) for n in range(64)]
        )
    )[-1]
    searchRange = maximum[1] * 16
    outfile.write(struct.pack(">H", searchRange))
    entrySelector = maximum[0]
    outfile.write(struct.pack(">H", entrySelector))
    rangeShift = WOFFHeader["numTables"] * 16 - searchRange
    outfile.write(struct.pack(">H", rangeShift))

    offset = outfile.tell()

    TableDirectoryEntries = []
    for i in range(0, WOFFHeader["numTables"]):
        TableDirectoryEntries.append(
            {
                "tag": struct.unpack(">I", infile.read(4))[0],
                "offset": struct.unpack(">I", infile.read(4))[0],
                "compLength": struct.unpack(">I", infile.read(4))[0],
                "origLength": struct.unpack(">I", infile.read(4))[0],
                "origChecksum": struct.unpack(">I", infile.read(4))[0],
            }
        )
        offset += 4 * 4

    for TableDirectoryEntry in TableDirectoryEntries:
        outfile.write(struct.pack(">I", TableDirectoryEntry["tag"]))
        outfile.write(struct.pack(">I", TableDirectoryEntry["origChecksum"]))
        outfile.write(struct.pack(">I", offset))
        outfile.write(struct.pack(">I", TableDirectoryEntry["origLength"]))
        TableDirectoryEntry["outOffset"] = offset
        offset += TableDirectoryEntry["origLength"]
        if (offset % 4) != 0:
            offset += 4 - (offset % 4)

    for TableDirectoryEntry in TableDirectoryEntries:
        infile.seek(TableDirectoryEntry["offset"])
        compressedData = infile.read(TableDirectoryEntry["compLength"])
        if TableDirectoryEntry["compLength"] != TableDirectoryEntry["origLength"]:
            uncompressedData = zlib.decompress(compressedData)
        else:
            uncompressedData = compressedData
        outfile.seek(TableDirectoryEntry["outOffset"])
        outfile.write(uncompressedData)
        offset = TableDirectoryEntry["outOffset"] + TableDirectoryEntry["origLength"]
        padding = 0
        if (offset % 4) != 0:
            padding = 4 - (offset % 4)
        outfile.write(bytearray(padding))


def convert(in_filename: Union[str, Path], out_filename: Union[str, Path]):
    with open(in_filename, mode="rb") as infile:
        with open(out_filename, mode="wb") as outfile:
            convert_streams(infile, outfile)


def discover_and_convert(source_dir: Path, target_dir: Path):
    for file in source_dir.glob("*.woff"):
        convert(file, target_dir / file.name.replace(".woff", ".otf"))
    for subdir in source_dir.glob("**/"):  # first subdir is the dir itself
        if subdir == source_dir:
            continue
        discover_and_convert(subdir, target_dir / subdir.name)


def main(argv: list[str]):
    if len(argv) == 1 or len(argv) > 3:
        print(
            "I convert *.woff files to *.otf files. (one at a time :)\n"
            "Usage: woff2otf.py web_font.woff|directory [converted_filename.otf|directory]\n"
            "If the target file name is omitted, it will be guessed. Have fun!\n"
        )
        return

    source = Path(argv[1]).resolve()
    target = Path(argv[2]) if len(argv) == 3 else None

    if source.is_dir():
        if target is None:
            target = source
        assert target.is_dir()
    else:
        if target is None:
            target = source.parent / source.name.replace(".woff", ".otf")
        assert target.is_file()

    if source.is_file():
        convert(source, target)
    else:
        discover_and_convert(source, target)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
