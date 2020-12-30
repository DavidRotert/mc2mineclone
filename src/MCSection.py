import os
import sys
import zlib
import nbt
import random
import time
import logging
import pprint
from io import BytesIO
import sqlite3

import mcvars
import serialize
from itemstack import *
from tile_entities import te_convert
from entities import e_convert

class InvalidRegionFileFormatException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

"""A 16x16x16 block section"""
class MCSection:
    
    def __init__(self, level_data, section, x, z, yslice, data_version, is_anvil=True):
        if is_anvil:
            # the x axis has to be inverted to convert to minetest (the chunk location is at the L lower corner, so subtract one or there would be 2 chunks at 0).
            # This converts the chunk location (node level data is converted by reverse_X_axis)
            self.pos = (-x - 1, yslice, z)
            if data_version < mcvars.NEW_REGION_FORMAT_VERSION:
                self.parse_anvil_nbt1_section(section)
            else:
                raise InvalidRegionFileFormatException("Cannot read region file for Minecraft version {}".format(data_version))
        else:
            self.pos = (x, yslice, z)
            # No luck, we have to convert
            self.parse_chunk_old_format(level_data, yslice)

        self.tile_entities = []
        for te in level_data["TileEntities"]:
            if (te["y"] >> 4) == yslice:
                t = te.copy()
                # Entity data stores it's own position information, so has to be modified independently in addition to other blocks.
                t["y"] &= 0xf
                t["y"] = t["y"] -16
                # within the chunk x position has to be inverted to convert to minetest:-
                if is_anvil:
                    t["x"] = self.pos[0] * 16 + 15 - t["x"] % 16
                self.tile_entities.append(t)

        self.entities = []
        for e in level_data["Entities"]:
            t = e.copy()
            self.entities.append(t)

    def parse_chunk_old_format(self, chunk, yslice):
        self.blocks = self.extract_slice(chunk["Blocks"], yslice)
        self.data = self.extract_slice_half_bytes(chunk["Data"], yslice)
        self.sky_light = self.extract_slice_half_bytes(chunk["SkyLight"], yslice)
        self.block_light = self.extract_slice_half_bytes(chunk["BlockLight"], yslice)

    def parse_anvil_nbt1_section(self, section):
        self.blocks = self.reverse_X_axis(section["Blocks"])
        self.data = self.expand_half_bytes(section["Data"])
        self.sky_light = self.expand_half_bytes(section["SkyLight"])
        self.block_light = self.expand_half_bytes(section["BlockLight"])


    @staticmethod
    def expand_half_bytes(l):
        # This function reverses x axis node order within each slice, and
        #   expands the 4bit sequences into 8bit sequences

        l3=[]
        for y in range(0, 2047, 128):
            for z in range(120, -1, -8):
            #for z in range(0, 127, 8):
                locSt=y+z
                l2 = l[locSt:locSt + 8]
                #for i in reversed(l2):
                for i in l2:
                    l3.append(i & 0xf)
                    l3.append((i >> 4) & 0xf)
        return l3


    @staticmethod
    def reverse_X_axis(l):
        # Anvil format is YZX ((y * 16 + z) * 16 + x)
        # block data is actually u12 per data point (ie per node)
        # but is split into u8 (='blocks') dealt with in reverse_X_axis() and u4 (='data') dealt with in expand_half_bytes()
        # NB data, skylight and blocklight are only 4bits of data

        # To convert minecraft to minetest coordinates you must invert the x order while leaving y and z the same
        # 2017/02/14 : In order to have north on the good side, we'll rather invert Z axis
        l3=[]
        for y in range(0, 4095, 256):
            #for z in range(0, 255, 16):
            for z in range(240, -1, -16):
                locSt=y+z
                l2 = l[locSt:locSt + 16]
                #for i in reversed(l2):
                for i in l2:
                    l3.append(i)
        return l3

    @staticmethod
    def extract_slice(data, yslice):
        data2 = [0] * 4096
        k = yslice << 4
        k2 = 0
        # Beware: impossible to understand code
        # Sorry, but it has to be as fast as possible,
        # as it is one bottleneck
        # Basically: order is changed from XZY to YZX
        for y in range(16):
            for z in range(16):
                for x in range(16):
                    data2[k2] = data[k]
                    k2 += 1
                    k += 2048
                k = (k & 0x7ff) + 128
            k = (k & 0x7f) + 1
        return data2

    @staticmethod
    def extract_slice_half_bytes(data, yslice):
        data2 = [0] * 4096
        k = yslice << 3
        k2 = 0
        k3 = 256 # One layer above the previous one
        # Beware: impossible to understand code
        # Even worse than before: that time we've got
        # to extract half bytes at the same time
        # Again, order is changed from XZY to YZX
        for y in range(0, 16, 2): # 2 values for y at a time
            for z in range(16):
                for x in range(16):
                    data2[k2] = data[k] & 0xf
                    data2[k3] = (data[k] >> 4) & 0xf
                    k2 += 1
                    k3 += 1
                    k += 1024
                k = (k & 0x3ff) + 64
            k = (k & 0x3f) + 1
            k2 += 256 # Skip a layer
            k3 += 256
        return data2