import os
import sys
import zlib
import nbt
import random
import time
import logging
from io import BytesIO
import sqlite3

import serialize
from itemstack import *
from tile_entities import te_convert
from entities import e_convert
from block import *

"""Minecraft map"""
class MCMap:
    REGION_CHUNK_LENGTH = 32

    """Minecraft Map representation

    Args:
        world_path: path to world directory
    """
    def __init__(self, world_path):
        self.world_path = os.path.join(world_path, "region")
        self.chunk_positions = []

        # Parse region files (Region and Anvil) files in "region" folder
        for ext in ["mca", "mcr"]:
            filenames = [i for i in os.listdir(self.world_path)
                         if i.endswith("." + ext)]
            if len(filenames) > 0:
                self.ext = ext
                break

        chunkCountA = 0
        chunkCountB = 0
        for filename in filenames:
            chunkCountA += 1
            # Parse filename r.[region X].[region Z].mc(a/r)
            _r, regionXstr, regionZstr, _ext = filename.split(".")

            startChunkX = int(regionXstr) * MCMap.REGION_CHUNK_LENGTH
            startChunkZ = int(regionZstr) * MCMap.REGION_CHUNK_LENGTH

            with open(os.path.join(self.world_path, filename), "rb") as regionFile:
                for regionChunkXPos in range(startChunkX, startChunkX + MCMap.REGION_CHUNK_LENGTH):
                    for regionChunkZPos in range(startChunkZ, startChunkZ + MCMap.REGION_CHUNK_LENGTH):
                        offset = ((regionChunkXPos % MCMap.REGION_CHUNK_LENGTH) +
                                  MCMap.REGION_CHUNK_LENGTH * 
                                    (regionChunkZPos % MCMap.REGION_CHUNK_LENGTH)
                                ) * 4
                        regionFile.seek(offset)
                        if serialize.bytesToInt(regionFile.read(3)) != 0:
                            self.chunk_positions.append((regionChunkXPos, regionChunkZPos))
                            chunkCountB += 1

    def getChunk(self, chkx, chkz):
        return MCChunk(chkx, chkz, self.world_path, self.ext)

    def getBlocksIterator(self):
        num_chunks = len(self.chunk_positions)
        chunk_ix = 0
        t0 = time.time()
        for chkx, chkz in self.chunk_positions:
            if chunk_ix % 10 == 0:
                if chunk_ix > 0:
                    td = time.time() - t0                     # wall clock time spent
                    tr = ((num_chunks * td) / chunk_ix) - td  # time remaining
                    eta = time.strftime("%H:%M:%S", time.gmtime(tr))
                else:
                    eta = "??:??:??"
                print('Processed %d / %d chunks, ETA %s h:m:s' %
                      (chunk_ix, num_chunks, eta), end='\r')
                sys.stdout.flush()
            chunk_ix += 1
            blocks = self.getChunk(chkx, chkz).blocks
            for block in blocks:
                yield block
        print()
