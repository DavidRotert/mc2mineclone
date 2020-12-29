import os
import sys
import zlib
import nbt
import random
import time
import logging
from io import BytesIO
import sqlite3

from MCMap import MCMap
from MCBlock import MCBlock
import serialize
from itemstack import *
from tile_entities import te_convert
from entities import e_convert

"""A chunk (16x16x256 blocks)"""
class MCChunk:
    def __init__(self, x, z, path, ext):
        filename = os.path.join(path, "r.{}.{}.{}".format(x // MCMap.REGION_CHUNK_LENGTH, z // MCMap.REGION_CHUNK_LENGTH, ext))
        with open(filename, "rb") as f:
            offset1 = ((x % MCMap.REGION_CHUNK_LENGTH) + MCMap.REGION_CHUNK_LENGTH * (z % MCMap.REGION_CHUNK_LENGTH)) * 4
            f.seek(offset1)
            offset2 = serialize.bytesToInt(f.read(3)) << 12
            f.seek(offset2)
            length = serialize.bytesToInt(f.read(4))
            compression_type = serialize.bytesToInt(f.read(1))
            data = f.read(length - 1) # 1 byte for compression_type
        if compression_type == 1: # Gzip
            unpackedData = zlib.decompress(data, 15 + 16)
        elif compression_type == 2: # Zlib
            unpackedData = zlib.decompress(data)
        else:
            raise ValueError("Unsupported compression type")

        nbt_data = nbt.read(unpackedData)['']['Level']

        self.blocks = []
        if ext == "mca":
            # Anvil file format
            for section in nbt_data["Sections"]:
                self.blocks.append(MCBlock(nbt_data, (x, z), section["Y"], True))
        else:
            for yslice in range(8):
                self.blocks.append(MCBlock(nbt_data, (x, z), yslice, False))