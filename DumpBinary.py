
""" dump binary stream into hexlify """

def dumpBinary(data):
    addr = 0
    buf = ""
    for i in range(len(data) / 16):
        buf += "%04X: " % addr
        for j in range(16):
            buf += "%02X " % ord(data[addr+j])
            if (j == 7):
                buf += " "
        buf += " "
        for j in range(16):
            if ((ord(data[addr+j]) >= 0x20) and (ord(data[addr+j]) < 0x7f)):
                buf += data[addr+j]
            else:
                buf += "."
        addr += 16
        buf += "\n"
    remain = (len(data) % 16)
    buf += "%04X: " % addr
    if (remain > 0):
        for j in range(remain):
            buf += "%02X " % ord(data[addr+j])
            if (j == 7):
                buf += " "
        for j in range(16-remain):
            buf += "   "
            if (j+remain == 7):
                buf += " "
        buf += " "
        for j in range(remain):
            if ((ord(data[addr+j]) >= 0x20) and (ord(data[addr+j]) < 0x7f)):
                buf += data[addr+j]
            else:
                buf += "."
        for j in range(16-remain):
            buf += " "
    buf += "\n\n"
    return buf


if (__name__ == "__main__"):
    print dumpBinary("0123456789abcdefg0123456789abcdefg")
    
