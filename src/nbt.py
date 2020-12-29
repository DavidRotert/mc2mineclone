import struct

def _read_tag(bytes, index, tag):
    # end, byte, short, int, long, float, double
    if tag <= 6:
        binLength = (None, 1, 2, 4, 8, 4, 8)[tag]
        value = struct.unpack(">" + (None, "b", "h", "i", "q", "f", "d")[tag],
                                bytes[index:index + binLength])[0]
        index += binLength
        return value, index
    # byte array
    elif tag == 7:
        binLength, index = _read_tag(bytes, index, 3)
        value = list(struct.unpack(">" + str(binLength) + "B", bytes[index:index +binLength]))
        index += binLength
        return value, index
    # string
    elif tag == 8:
        binLength, index = _read_tag(bytes, index, 2)
        value = bytes[index:index + binLength].decode("utf-8")
        index += binLength
        return value, index
    # list
    elif tag == 9:
        tagid = bytes[index]
        index += 1
        binLength, index = _read_tag(bytes, index, 3)
        value = []
        for i in range(binLength):
            v, index = _read_tag(bytes, index, tagid)
            value.append(v)
        return value, index
    # Compound
    elif tag == 10:
        return _read_named(bytes, index)
    # int array
    elif tag == 11:
        binLength, index = _read_tag(bytes, index, 3)
        value = list(struct.unpack(">" + str(binLength) + "i", bytes[index:index + 4 * binLength]))
        index += 4 * binLength
        return value, index
    elif tag == 12:
        binLengt, index = _read_tag(bytes, index, 3)
        value = list(struct.unpack(">" + str(binLengt) + "q", bytes[index:index + 8 * binLengt]))
        index += 8 * binLengt
        return value, index
    else:
        raise Exception("Unknown tag: " + str(tag))

def _read_named(bytes, index):
    data = {}
    while True:
        if index >= len(bytes):
            return data, index
        tag = bytes[index]
        index += 1
        if tag == 0:
            return data, index
        name, index = _read_tag(bytes, index, 8)
        value, index = _read_tag(bytes, index, tag)
        data[name] = value

def read(bytes):
    return _read_named(bytes, 0)[0]
