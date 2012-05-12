#!/usr/bin/python3
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

infile  = open(sys.argv[1], mode='rb')
outfile = open(sys.argv[2], mode='wb')

WOFFHeader = {'signature': struct.unpack(">I", infile.read(4))[0],
              'flavor': struct.unpack(">I", infile.read(4))[0],
              'length': struct.unpack(">I", infile.read(4))[0],
              'numTables': struct.unpack(">H", infile.read(2))[0],
              'reserved': struct.unpack(">H", infile.read(2))[0],
              'totalSfntSize': struct.unpack(">I", infile.read(4))[0],
              'majorVersion': struct.unpack(">H", infile.read(2))[0],
              'minorVersion': struct.unpack(">H", infile.read(2))[0],
              'metaOffset': struct.unpack(">I", infile.read(4))[0],
              'metaLength': struct.unpack(">I", infile.read(4))[0],
              'metaOrigLength': struct.unpack(">I", infile.read(4))[0],
              'privOffset': struct.unpack(">I", infile.read(4))[0],
              'privLength': struct.unpack(">I", infile.read(4))[0]}

outfile.write(struct.pack(">I", WOFFHeader['flavor']));
outfile.write(struct.pack(">H", WOFFHeader['numTables']));
maximum = list(filter(lambda x: x[1] < WOFFHeader['numTables'], [(n, n**2) for n in range(64)]))[-1]; 
searchRange = maximum[1] * 16
outfile.write(struct.pack(">H", searchRange));
entrySelector = maximum[0]
outfile.write(struct.pack(">H", entrySelector));
rangeShift = WOFFHeader['numTables'] * 16 -  searchRange;
outfile.write(struct.pack(">H", rangeShift));

offset = outfile.tell()

TableDirectoryEntries = []
for i in range(0, WOFFHeader['numTables']):
    TableDirectoryEntries.append({'tag': struct.unpack(">I", infile.read(4))[0],
                           'offset': struct.unpack(">I", infile.read(4))[0],
                           'compLength': struct.unpack(">I", infile.read(4))[0],
                           'origLength': struct.unpack(">I", infile.read(4))[0],
                           'origChecksum': struct.unpack(">I", infile.read(4))[0]})
    offset += 4*4
    
for TableDirectoryEntry in TableDirectoryEntries:   
    outfile.write(struct.pack(">I", TableDirectoryEntry['tag']))
    outfile.write(struct.pack(">I", TableDirectoryEntry['origChecksum']))
    outfile.write(struct.pack(">I", offset))
    outfile.write(struct.pack(">I", TableDirectoryEntry['origLength']))
    TableDirectoryEntry['outOffset'] = offset
    offset += TableDirectoryEntry['origLength']
    if (offset % 4) != 0:
        offset += 4 - (offset % 4)
        
for TableDirectoryEntry in TableDirectoryEntries:
    infile.seek(TableDirectoryEntry['offset'])
    compressedData = infile.read(TableDirectoryEntry['compLength'])
    if TableDirectoryEntry['compLength'] != TableDirectoryEntry['origLength']:
        uncompressedData = zlib.decompress(compressedData)
    else:
        uncompressedData = compressedData
    outfile.seek(TableDirectoryEntry['outOffset'])
    outfile.write(uncompressedData)
    offset = TableDirectoryEntry['outOffset'] + TableDirectoryEntry['origLength'];
    padding = 0
    if (offset % 4) != 0:
        padding = 4 - (offset % 4)
    outfile.write(bytearray(padding));

    