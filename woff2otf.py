#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "brotli",
# ]
# ///
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


# https://www.w3.org/TR/WOFF2/#FileStructure
def ReadUIntBase128(infile):
    accum = 0

    for i in range(5):
        data_byte = struct.unpack(">B", infile.read(1))[0]

        # No leading 0's
        if i == 0 and data_byte == 0x80:
            raise RuntimeError()

        # If any of top 7 bits are set then << 7 would overflow
        if accum & 0xFE000000:
            raise RuntimeError()

        accum = (accum << 7) | (data_byte & 0x7F)

        # Spin until most significant bit of data byte is false
        if data_byte & 0x80 == 0:
            return accum

    raise RuntimeError()


def convert_woff_1_0(infile, outfile):
    WOFFHeader = {
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

KNOWN_TAGS = {
    0: b'cmap', 1: b'head', 2: b'hhea', 3: b'hmtx', 4: b'maxp', 5: b'name',
    6: b'OS/2', 7: b'post', 8: b'cvt', 9: b'fpgm', 10: b'glyf', 11: b'loca',
    12: b'prep', 13: b'CFF', 14: b'VORG', 15: b'EBDT', 16: b'EBLC', 17: b'gasp',
    18: b'hdmx', 19: b'kern', 20: b'LTSH', 21: b'PCLT', 22: b'VDMX', 23: b'vhea',
    24: b'vmtx', 25: b'BASE', 26: b'GDEF', 27: b'GPOS', 28: b'GSUB', 29: b'EBSC',
    30: b'JSTF', 31: b'MATH', 32: b'CBDT', 33: b'CBLC', 34: b'COLR', 35: b'CPAL',
    36: b'SVG', 37: b'sbix', 38: b'acnt', 39: b'avar', 40: b'bdat', 41: b'bloc',
    42: b'bsln', 43: b'cvar', 44: b'fdsc', 45: b'feat', 46: b'fmtx', 47: b'fvar',
    48: b'gvar', 49: b'hsty', 50: b'just', 51: b'lcar', 52: b'mort', 53: b'morx',
    54: b'opbd', 55: b'prop', 56: b'trak', 57: b'Zapf', 58: b'Silf', 59: b'Glat',
    60: b'Gloc', 61: b'Feat', 62: b'Sill', 63: b'arbitrary tag follows'
}

def convert_woff_2_0(infile, outfile):
    WOFF2Header = {
        "flavor": struct.unpack(">I", infile.read(4))[0],
        "length": struct.unpack(">I", infile.read(4))[0],
        "numTables": struct.unpack(">H", infile.read(2))[0],
        "reserved": struct.unpack(">H", infile.read(2))[0],
        "totalSfntSize": struct.unpack(">I", infile.read(4))[0],
        "totalCompressedSize": struct.unpack(">I", infile.read(4))[0],
        "majorVersion": struct.unpack(">H", infile.read(2))[0],
        "minorVersion": struct.unpack(">H", infile.read(2))[0],
        "metaOffset": struct.unpack(">I", infile.read(4))[0],
        "metaLength": struct.unpack(">I", infile.read(4))[0],
        "metaOrigLength": struct.unpack(">I", infile.read(4))[0],
        "privOffset": struct.unpack(">I", infile.read(4))[0],
        "privLength": struct.unpack(">I", infile.read(4))[0],
    }

    def _transformed(tag, transform):
        if tag in {"glyf", "loca"}:
            return transform != 3
        else:
            return transform != 0

    TableDirectoryEntries = []
    for i in range(0, WOFF2Header["numTables"]):
        flags = struct.unpack(">B", infile.read(1))[0]
        # Bits [0..5] contain an index to the "known tag" table, which represents tags likely to appear in fonts.
        # If the tag is not present in this table, then the value of this bit field is 63
        known_tag = flags & 0x3f
        if known_tag == 0x63:
            tag = struct.unpack(">cccc", infile.read(4))[0]
        else:
            tag = KNOWN_TAGS[known_tag]

        transform = flags >> 6

        origLength = ReadUIntBase128(infile)

        transformLength = None
        if _transformed(tag, transform):
            transformLength = ReadUIntBase128(infile)

        entry = {
            "transform": transform,
            "tag": tag,
            "origLength": origLength,
            "transformLength": transformLength
        }
        print(entry)
        TableDirectoryEntries.append(entry)


def convert_streams(infile, outfile):
    signature = struct.unpack(">I", infile.read(4))[0].to_bytes(4, byteorder="big")

    if signature == b"wOFF":
        convert_woff_1_0(infile, outfile)
    elif signature == b"wOF2":
        convert_woff_2_0(infile, outfile)
    else:
        raise RuntimeError("Unknown file format")


def convert(infilename, outfilename):
    with open(infilename, mode="rb") as infile, open(outfilename, mode="wb") as outfile:
        convert_streams(infile, outfile)


def main(argv):
    if len(argv) == 1 or len(argv) > 3:
        print(
            "I convert *.woff files to *.otf files. (one at a time :)\n"
            "Usage: woff2otf.py web_font.woff [converted_filename.otf]\n"
            "If the target file name is omitted, it will be guessed. Have fun!\n"
        )
        return

    source_file_name = argv[1]
    if len(argv) == 3:
        target_file_name = argv[2]
    else:
        target_file_name = source_file_name.rsplit(".", 1)[0] + ".otf"

    convert(source_file_name, target_file_name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
