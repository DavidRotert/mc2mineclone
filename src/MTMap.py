import sqlite3
import os

from MTBlock import MTBlock

class MTMap:
    def __init__(self, path):
        self.world_path = path
        self.blocks = []

    @staticmethod
    def getBlockAsInteger(p):
        return p[0] + 4096 * (p[1] + 4096 * p[2])

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
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS `blocks` (\
            `pos` INT NOT NULL PRIMARY KEY, `data` BLOB);")

        num_saved = 0
        for block in self.blocks:
            if num_saved % 100 == 0:
                #print("Saved", num_saved, "blocks")
                conn.commit()
            num_saved += 1
            cursor.execute("INSERT INTO blocks VALUES (?,?)",
                        (self.getBlockAsInteger((-block.pos[0],block.pos[1],-block.pos[2])),
                        block.save()))

        conn.commit()
        conn.close()