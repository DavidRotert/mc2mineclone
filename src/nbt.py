import struct

from mcvars import *

def _read_tag(bytes, index, tag):
    # end, byte, short, int, long, float, double
    if tag <= NBTTags.DOUBLE_TAG:
        binLength = (NBTTags.END_LENGTH, NBTTags.BYTE_LENGTH, NBTTags.SHORT_LENGTH, NBTTags.INT_LENGTH,
                NBTTags.LONG_LENGTH, NBTTags.FLOAT_LENGTH, NBTTags.DOUBLE_LENGTH)[tag]
        value = struct.unpack(">" + (None, "b", "h", "i", "q", "f", "d")[tag],
                                bytes[index:index + binLength])[0]
        index += binLength
        return value, index
    # byte array
    elif tag == NBTTags.BYTE_ARRAY_TAG:
        binLength, index = _read_tag(bytes, index, NBTTags.INT_TAG)
        value = list(struct.unpack(">" + str(binLength) + "B", bytes[index:index +binLength]))
        index += binLength
        return value, index
    # string
    elif tag == NBTTags.STRING_TAG:
        binLength, index = _read_tag(bytes, index, NBTTags.SHORT_TAG)
        value = bytes[index:index + binLength].decode("utf-8")
        index += binLength
        return value, index
    # list
    elif tag == NBTTags.LIST_TAG:
        tagid = bytes[index]
        index += 1
        binLength, index = _read_tag(bytes, index, NBTTags.INT_TAG)
        value = []
        for i in range(binLength):
            v, index = _read_tag(bytes, index, tagid)
            value.append(v)
        return value, index
    # compound
    elif tag == NBTTags.COMPOUND_TAG:
        return _read_compound(bytes, index)
    # int array
    elif tag == NBTTags.INT_ARRAY_TAG:
        binLength, index = _read_tag(bytes, index, NBTTags.INT_TAG)
        value = list(struct.unpack(">" + str(binLength) + "i", bytes[index:index + NBTTags.INT_LENGTH * binLength]))
        index += NBTTags.INT_LENGTH * binLength
        return value, index
    elif tag == NBTTags.LONG_ARRAY_TAG:
        binLengt, index = _read_tag(bytes, index, NBTTags.INT_TAG)
        value = list(struct.unpack(">" + str(binLengt) + "q", bytes[index:index + NBTTags.LONG_LENGTH * binLengt]))
        index += NBTTags.LONG_LENGTH * binLengt
        return value, index
    else:
        raise Exception("Unknown tag: " + str(tag))

def _read_compound(bytes, index):
    data = {}
    while True:
        if index >= len(bytes):
            return data, index
        tag = bytes[index]
        index += 1
        if tag == NBTTags.END_TAG:
            return data, index
        name, index = _read_tag(bytes, index, NBTTags.STRING_TAG)
        value, index = _read_tag(bytes, index, tag)
        data[name] = value

def read(bytes):
    return _read_compound(bytes, 0)[0]
