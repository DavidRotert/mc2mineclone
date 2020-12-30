import os
import sys
import zlib
import nbt
import random
import time
import logging
from io import BytesIO
import sqlite3
from serialize import *
from itemstack import *
from tile_entities import te_convert
from entities import e_convert
from MTBlock import MTBlock

logger = logging.getLogger('block')

class MTMap:
    def __init__(self, path):
        self.world_path = path
        self.blocks = []

    @staticmethod
    def getBlockAsInteger(p):
        return p[0]+4096*(p[1]+4096*p[2])

    @staticmethod
    def fromMCMapBlocksIterator(mcmap, name_id_mapping, conversion_table):
        for mcblock in mcmap.getBlocksIterator():
            mtblock = MTBlock(name_id_mapping)
            mtblock.fromMCBlock(mcblock, conversion_table)
            yield mtblock

    def fromMCMap(self, mcmap, nimap, ct):
        self.blocks = self.fromMCMapBlocksIterator(mcmap, nimap, ct)

    def save(self):
        conn = sqlite3.connect(os.path.join(self.world_path, "map.sqlite"))
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS `blocks` (\
            `pos` INT NOT NULL PRIMARY KEY, `data` BLOB);")

        num_saved = 0
        for block in self.blocks:
            if num_saved%100 == 0:
                #print("Saved", num_saved, "blocks")
                conn.commit()
            num_saved += 1
            cur.execute("INSERT INTO blocks VALUES (?,?)",
#                        (self.getBlockAsInteger((-block.pos[0],block.pos[1],block.pos[2])),
                        (self.getBlockAsInteger((-block.pos[0],block.pos[1],-block.pos[2])),
                        block.getBlockData()))

        conn.commit()
        conn.close()


# if __name__ == "__main__":
#     # Tests
#     from random import randrange
#     t = [randrange(256) for i in range(2048*8)]
#     assert(MCBlock.extract_slice(MCBlock.expand_half_bytes(t), 0)
#           == MCBlock.extract_slice_half_bytes(t, 0))

#     from time import time
#     t0 = time()
#     s1 = MCBlock.extract_slice(MCBlock.expand_half_bytes(t), 1)
#     print(time()-t0)
#     t0 = time()
#     s2 = MCBlock.extract_slice_half_bytes(t, 1)
#     print(time()-t0)
#     assert(s1 == s2)
