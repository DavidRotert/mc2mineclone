def writeU8(out, u8):
    out.write(bytes((u8 & 0xff,)))

def writeU16(out, u16):
    out.write(bytes(((u16 >> 8) & 0xff,)))
    out.write(bytes((u16 & 0xff,)))

def writeU32(os, u32):
    os.write(bytes(((u32 >> 24) & 0xff,)))
    os.write(bytes(((u32 >> 16) & 0xff,)))
    os.write(bytes(((u32 >> 8) & 0xff,)))
    os.write(bytes((u32 & 0xff,)))

def writeString(out, s):
    b = bytes(s, "utf-8")
    writeU16(out, len(b))
    out.write(b)

def writeLongString(out, s):
    b = bytes(s, "utf-8")
    writeU32(out, len(b))
    out.write(b)

def bytesToInt(b):
    s = 0
    for x in b:
        s = (s << 8) + x
    return s
