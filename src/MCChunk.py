import os
import sys
import zlib
import nbt
import random
import time
import logging
from io import BytesIO
import sqlite3
import json

import mcvars
from MCSection import MCSection
import serialize
from itemstack import *
from tile_entities import te_convert
from entities import e_convert

"""A chunk (16x16x256 blocks)"""
class MCChunk:
    def __init__(self, x, z, path, ext):
        filename = os.path.join(path, "r.{}.{}.{}".format(x // mcvars.REGION_CHUNK_LENGTH, z // mcvars.REGION_CHUNK_LENGTH, ext))
        with open(filename, "rb") as f:
            offset1 = ((x % mcvars.REGION_CHUNK_LENGTH) + mcvars.REGION_CHUNK_LENGTH * (z % mcvars.REGION_CHUNK_LENGTH)) * 4
            f.seek(offset1)
            offset2 = serialize.bytesToInt(f.read(3)) << 12
            f.seek(offset2)
            length = serialize.bytesToInt(f.read(4))
            compression_type = serialize.bytesToInt(f.read(1))
            # 1 byte for compression_type
            data = f.read(length - 1)
        # Gzip
        if compression_type == 1:
            unpackedData = zlib.decompress(data, 15 + 16)
        # Zlib
        elif compression_type == 2:
            unpackedData = zlib.decompress(data)
        else:
            raise ValueError("Unsupported compression type")

        nbt_data = nbt.read(unpackedData)
        level_data = nbt_data[""]["Level"]
        #with open("chunk.json", "w") as jsonf:
            #jsonf.write(json.dumps(nbt_data, indent=4))
        #sys.exit(0)

        self.blocks = []

        if ext == "mca":
            # Anvil file format
            for section in level_data["Sections"]:
                self.blocks.append(MCSection(level_data, section, x, z, section["Y"], True))
        elif ext == "mcr":
            # Old file format
            for yslice in range(8):
                self.blocks.append(MCSection(nbt_data, section, x, z, yslice, False))