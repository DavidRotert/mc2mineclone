import random
import zlib
from io import BytesIO

from itemstack import *
import serialize
from tile_entities import te_convert
from entities import e_convert

class MTBlock:
    def __init__(self, name_id_mapping):
        self.name_id_mapping = name_id_mapping
        self.content = [0] * 4096
        self.mcblockidentifier = [''] * 4096
        self.param1 = [0] * 4096
        self.param2 = [0] * 4096
        self.metadata = {}
        self.pos = (0, 0, 0)

    def fromMCBlock(self, mcblock, conversion_table):
        self.timers = []
        self.pos = (mcblock.pos[0], mcblock.pos[1] -4, mcblock.pos[2])
        content = self.content
        mcblockidentifier = self.mcblockidentifier
        param1 = self.param1
        param2 = self.param2
        blocks = mcblock.blocks
        data = mcblock.data
        skylight = mcblock.sky_light
        blocklight = mcblock.block_light

        # now load all the nodes in the 16x16x16 (=4096) block
        for i in range(4096):
            content[i], param2[i] = conversion_table[blocks[i]][data[i]]
            param1[i] = max(blocklight[i], skylight[i]) | (blocklight[i] << 4)
            mcblockidentifier[i] = str(blocks[i]) + ':' + str(data[i])

            def isdoor(b):
                return b == 64 or b == 71 or (b >= 193 and b <= 197)

            # water
            if (blocks[i] == 9 or blocks[i] == 11) and (data[i] == 0):
                content[i], param2[i] = conversion_table[blocks[i]][data[i]]
            elif blocks[i] >= 8 and blocks[i] <= 11:
                # nop, exit case
                pass
            # pressure plates - append mesecons node timer
            elif blocks[i] == 70 or blocks[i] == 72:
                self.timers.append(((i & 0xf) | ((i >> 4) & 0xf) << 8 |((i >> 8) & 0xf) << 4, 100, 0))
            # rotate lily pads randomly
            elif blocks[i] == 111:
                param2[i] = random.randint(0, 3)
            # grass of varying length randomly
            elif blocks[i] == 31 and data[i] == 1:
                content[i], param2[i] = conversion_table[931][random.randint(0, 4)]
            # fix doors based on top/bottom bits
            elif isdoor(blocks[i]) and data[i] < 8:  # bottom part
                above = i + 256
                if (above >= 4096):
                    pass
                    #logger.warning('Unable to fix door - top part is across block boundary! (%d >= 4096)' % above)
                elif isdoor(blocks[above]) and data[above] < 8:
                    pass
                    #logger.warning('Unable to fix door - bottom part 0x%x on top of bottom part 0x%x!', data[i], data[above])
                else:
                    d_right = data[above] & 1  # 0 - left, 1 - right
                    d_open = data[i] & 4       # 0 - closed, 1 - open
                    d_face = data[i] & 3       # n,e,s,w orientation
                    alt = 964
                    if blocks[i] == 71:
                        alt = 966
                    if blocks[i] == 193:
                        alt = 968
                    if blocks[i] == 194:
                        alt = 970
                    if blocks[i] == 195:
                        alt = 972
                    if blocks[i] == 196:
                        alt = 974
                    if blocks[i] == 197:
                        alt = 976
                    content[i], param2[i] = conversion_table[alt][d_face|d_open|(d_right<<3)]
                    if d_right == 1:
                        self.metadata[(i & 0xf, (i >> 8) & 0xf, (i >> 4) & 0xf)] = ({ "right": "1" }, {})
            elif isdoor(blocks[i]) and data[i] >= 8:  # top part
                below = i - 256
                if (below < 0):
                    pass
                    #logger.warning('Unable to fix door - bottom part is across block boundary! (%d < 0)' % below)
                elif isdoor(blocks[below]) and data[below] >= 8:
                    pass
                    #logger.warning('Unable to fix door - top part 0x%x below top part 0x%x!', data[i], data[below])
                else:
                    d_right = data[i] & 1      # 0 - left, 1 - right
                    d_open = data[below] & 4   # 0 - closed, 1 - open
                    d_face = data[below] & 3   # n,e,s,w orientation
                    alt = 965
                    if blocks[i] == 71:
                        alt = 967
                    if blocks[i] == 193:
                        alt = 969
                    if blocks[i] == 194:
                        alt = 971
                    if blocks[i] == 195:
                        alt = 973
                    if blocks[i] == 196:
                        alt = 975
                    if blocks[i] == 197:
                        alt = 977
                    content[i], param2[i] = conversion_table[alt][d_face|d_open|(d_right<<3)]
                    if d_right == 1:
                        self.metadata[(i & 0xf, (i>>8) & 0xf, (i>>4) & 0xf)] = ({ "right": "1" }, {})

            elif content[i]==0 and param2[i]==0 and not (blocks[i]==0):
                pass
                #logger.warning('Unknown Minecraft Block:' + str(mcblockidentifier[i]))     # This is the minecraft ID#/data as listed in map_content.txt

        for te in mcblock.tile_entities:
            id = te["id"]
            x, y, z = -te["x"] - 1, te["y"], -te["z"] - 1
            index = ((y&0xf)<<8)|((z&0xf)<<4)|(x&0xf)
            f = te_convert.get(id.lower(), lambda arg: (None, None, None)) # Do nothing if not found
            block, p2, meta = f(te)
            #logger.debug('EntityInfoPre: ' +str(te))
            #logger.debug('EntityInfoPost: ' +' y='+str(y)+' z='+str(z)+' x='+str(x)+' Meta:'+str(meta))
            # NB block and p2 never seems to be returned, but if this is important, then just change the above 'meta' to 'f(te)'

            if block != None:
                blocks[index] = block
            if p2 != None:
                param2[index] = p2
            if meta != None:
                try:
                    p = meta[0]["_plant"]
                    if p > 15:
                        content[index], param2[index] = conversion_table[941][p&0xf]
                    else:
                        content[index], param2[index] = conversion_table[940][p]
                except:
                    self.metadata[(x&0xf, y&0xf, z&0xf)] = meta

        for e in mcblock.entities:
            id = e["id"]
            f = e_convert.get(id.lower(), lambda arg: (None, None, None)) # Do nothing if not found
            block, p2, meta = f(e)

    def getBlockData(self):
        out = BytesIO()
        serialize.writeU8(out, 25) # Version

        #flags
        flags = 0x00
        if self.pos[1] < -1:
            flags |= 0x01       #is_underground
        flags |= 0x02           #day_night_differs
        flags |= 0x04           #lighting_expired
        flags |= 0x08           #generated
        serialize.writeU8(out, flags)

        serialize.writeU8(out, 2) # content_width
        serialize.writeU8(out, 2) # params_width

        cbuffer = BytesIO()
        # Bulk node data
        content = self.content
        k = 0
        nimap = {}
        rev_nimap = []
        first_free_content = 0
        for z in range(16):
            for y in range(16):
                for x in range(16):
                    #writeU16(cbuffer, content[k])
                    c = content[k]
                    if c in nimap:
                        serialize.writeU16(cbuffer, nimap[c])
                    else:
                        nimap[c] = first_free_content
                        serialize.writeU16(cbuffer, first_free_content)
                        rev_nimap.append(c)
                        first_free_content += 1
                    k += 1
                k += (256 - 16)
            k += (16 - (16 * 256))
        param1 = self.param1
        k = 0
        for z in range(16):
            for y in range(16):
                for x in range(16):
                    serialize.writeU8(cbuffer, param1[k])
                    k += 1
                k += (256 - 16)
            k += (16 - (16 * 256))
        param2 = self.param2
        k = 0
        for z in range(16):
            for y in range(16):
                for x in range(16):
                    serialize.writeU8(cbuffer, param2[k])
                    k += 1
                k += (256 - 16)
            k += (16 - (16 * 256))
        out.write(zlib.compress(cbuffer.getvalue()))

        # Nodemeta
        meta = self.metadata

        cbuffer = BytesIO()
        serialize.writeU8(cbuffer, 1) # Version
        serialize.writeU16(cbuffer, len(meta))
        for pos, data in meta.items():
            serialize.writeU16(cbuffer, (pos[2] << 8) | (pos[1] << 4) | pos[0])
            serialize.writeU32(cbuffer, len(data[0]))
            for name, val in data[0].items():
                serialize.writeString(cbuffer, name)
                serialize.writeLongString(cbuffer, str(val))
            serialize_inv(cbuffer, data[1])
        out.write(zlib.compress(cbuffer.getvalue()))

        # Static objects
        serialize.writeU8(out, 0) # Version
        serialize.writeU16(out, 0) # Number of objects

        # Timestamp
        serialize.writeU32(out, 0xffffffff) # BLOCK_TIMESTAMP_UNDEFINED

        # Name-ID mapping
        serialize.writeU8(out, 0) # Version
        serialize.writeU16(out, len(rev_nimap))
        for i in range(len(rev_nimap)):
            serialize.writeU16(out, i)
            serialize.writeString(out, self.name_id_mapping[rev_nimap[i]])

        # Node timer
        serialize.writeU8(out, 2+4+4) # Timer data len
        serialize.writeU16(out, len(self.timers)) # Number of timers
        if len(self.timers) > 0:
            pass
            #logger.info('wrote ' + str(len(self.timers)) + ' node timers')
        for i in range(len(self.timers)):
            serialize.writeU16(out, self.timers[i][0])
            serialize.writeU32(out, self.timers[i][1])
            serialize.writeU32(out, self.timers[i][2])

        return out.getvalue()
