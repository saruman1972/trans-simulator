# module for miscellaneous pin/mac calc

import string
import pyDes
from binascii import *

def blockXOR(d1, d2, blockLen=8):
    buf = ""
    for i in range(blockLen):
        buf += chr(ord(d1[i]) ^ ord(d2[i]))
    return buf

def calcMac(key, data, retlen=4):
    print "key=%s,macBlock=\n%s|\nhex(macBlock=\n%s|" % (hexlify(key), data, hexlify(data))
    if len(key) > 8:
        k = pyDes.triple_des(key)
    else:
        k = pyDes.des(key)
    length = len(data)
    r = length % 8
    b = length / 8
    if (r != 0):
        b = b + 1
        data += "\0" * (8-r)
        print r
    print hexlify(data) + "!!!!!"
    mac = "\0\0\0\0\0\0\0\0"
    for i in range(b):
        t = data[i*8 : (i+1)*8]
        t = blockXOR(mac, t)
        mac = k.encrypt(t)
        print "mac=%s" % (hexlify(mac))
    return mac[:retlen]

def makePinBlock(pan, pin):
    """
        pan -- primary account number
        pin -- personal identification number
    """

    if len(pan) == 0:
        return ' '*8

    pinblock = '0' + str(len(pin)) + pin + 'F'*(16-2-len(pin))
    serial = '0000' + pan[-13:-1]
    a = unhexlify(pinblock)
    b = unhexlify(serial)
    buf = ""
    for i in range(8):
        buf += chr(ord(a[i]) ^ ord(b[i]))

    return buf

def extractPIN(pan, pinblock):
    """
        pan -- primary account number
        pinblock -- pin block
    """

    if len(pinblock) == 0:
        pinblock = unhexlify("0000000000000000")
    serial = '0000' + pan[-13:-1]
    a = pinblock
    b = unhexlify(serial)
    print "a=",a,"len=",len(a)
    print "b=",b,"len=",len(b)
    buf = ""
    for i in range(8):
        buf += chr(ord(a[i]) ^ ord(b[i]))

    buf = hexlify(buf)
    pin_len = string.atoi(buf[:2])
    if pin_len > 6:
        pin_len = 6

    return buf[2:2+pin_len]

def String_to_BitList(data):
    """Turn the string data, into a list of bits (1, 0)'s"""
    l = len(data) * 8
    result = [0] * l
    pos = 0
    for c in data:
        i = 7
        ch = ord(c)
        while i >= 0:
            if ch & (1 << i) != 0:
                result[pos] = 1
            else:
                result[pos] = 0
            pos += 1
            i -= 1

    return result

def BitList_to_String(data):
    """Turn the list of bits -> data, into a string"""
    result = ''
    pos = 0
    c = 0
    while pos < len(data):
        c += data[pos] << (7 - (pos % 8))
        if (pos % 8) == 7:
            result += chr(c)
            c = 0
        pos += 1

    return result

def padDataBlock(data, moduler=8):
    """ padding data to 8bytes block to calc MAC..."""
    data += chr(0x80)
    remain = len(data) % moduler
    if remain > 0:
        padLen = moduler - len(data) % moduler
        data += '\x00' * padLen
    return data

def icCalcMac(key, data, retlen=4):
    print "key=%s,macBlock=\n%s|\nhex(macBlock=\n%s|" % (hexlify(key), data, hexlify(data))
    if len(key) > 8:
        k = pyDes.des(key[:8])
        kFinal = pyDes.des(key[8:16])
    else:
        k = pyDes.des(key)
    length = len(data)
    r = length % 8
    b = length / 8
    if (r != 0):
        b = b + 1
        data += "\0" * (8-r)
        print r
    print hexlify(data) + "!!!!!"
    mac = "\0\0\0\0\0\0\0\0"
    for i in range(b):
        t = data[i*8 : (i+1)*8]
        t = blockXOR(mac, t)
        mac = k.encrypt(t)
        print "mac=%s" % (hexlify(mac))
    if len(key) > 8:
        mac = kFinal.decrypt(mac)
        print "last mac=%s" % (hexlify(mac))
        mac = k.encrypt(mac)
        print "last mac=%s" % (hexlify(mac))
    return mac[:retlen]

def icKeyDerivation(mk, pan, pan_sn):
    print "mk=" + hexlify(mk)
    k = pyDes.triple_des(mk)
    data = pan + pan_sn
    if len(data) >= 16:
        data = data[-16:]
    else:
        padLen = 16 - len(data) % 16
        data = '0' * padLen + data
    data = unhexlify(data)
    r = blockXOR(data, '\xFF'*8)
    return k.encrypt(data) + k.encrypt(r)

def icSessionKey(udk, atc):
    k = pyDes.triple_des(udk)
    l = '\x00' * 6 + atc
    r = '\x00' * 6 + blockXOR(atc, '\xFF\xFF', 2)
    print "l="+hexlify(l)+"\n"
    print "r="+hexlify(r)+"\n"
    return k.encrypt(l) + k.encrypt(r)

def generateAC(tags, mk, pan, pan_sn, atc, tagObj):
    """ generate ARQC/AAC/TC"""
    data = ""
    for tag in tags:
        if tag == '\x9F\x10':
            data += tagObj[tag][3:7]    # CVR
        else:
            data += tagObj[tag]
    sessionKey = icSessionKey(icKeyDerivation(mk, pan, pan_sn), atc)
    print "generateAC:block=" + hexlify(data)
    block = padDataBlock(data)
    return icCalcMac(sessionKey, block, 8)

def unpackScript(script):
    cla = script[0]
    ins = script[1]
    p1 = script[2]
    p2 = script[3]
    lc = script[4]
    data = script[5:-4]
    mac = script[-4:]
    return (cla, ins, p1, p2, lc, data, mac)

def generateScriptMAC(mk_smi, pan, pan_sn, ac, atc, cla, ins, p1, p2, lc, data):
    block = cla + ins + p1 + p2 + lc + atc + ac + data
    block = padDataBlock(block)
    sessionKey = icSessionKey(icKeyDerivation(mk_smi, pan, pan_sn), atc)
    print "sessionKey=" + hexlify(sessionKey) + "\n"
    return icCalcMac(sessionKey, block, 8)

def generateARPC(mk, pan, pan_sn, atc, arqc, resp_cd):
    print "ARPC:mk="+hexlify(mk)+",arqc="+hexlify(arqc)+",atc="+hexlify(atc)+",resp_cd="+resp_cd
    sessionKey = icSessionKey(icKeyDerivation(mk, pan, pan_sn), atc)
    print "sessionKey="+hexlify(sessionKey)
    k = pyDes.triple_des(sessionKey)
    arpc =  k.encrypt(blockXOR(arqc, resp_cd+'\x00\x00\x00\x00\x00\x00'))
    print "ARPC="+hexlify(arpc)
    return arpc
    

    
if (__name__ == "__main__"):
    import sys
#    print calcMac(unhexlify("04C7BA865EECA85E"), "1203171541 000002 101 12345678")
    pan = '6282640000000421'
    pin = '123456'
    pinblock = makePinBlock(pan, pin)
    print 'pinblock=', hexlify(pinblock)
    key = pyDes.triple_des(unhexlify('EFCDAB1896745230EFCDAB1896745230'))
    print hexlify(key.encrypt(pinblock))
    sys.exit(0)

    import IsoFieldDef

    mk = '1234567890ABCDEF1234567890ABCDEF'
    pan = '4026741234567890'
    pan_sn = '01'
    atc = '\x00\x01'
    tags = {}
    tags['\x9F\x02'] = unhexlify('000000010000')
    tags['\x9F\x03'] = unhexlify('000000010000')
    tags['\x9F\x1A'] = unhexlify('156F')
    tags['\x95'] = '\x00'*5
    tags['\x5F\x2A'] = unhexlify('156F')
    tags['\x9A'] = unhexlify('110724')
    tags['\x9C'] = unhexlify('00')
    tags['\x9F\x37'] = unhexlify('1234')
    tags['\x82'] = unhexlify('0000')
    tags['\x9F\x36'] = unhexlify('0001')
    tags['\x9F\x10'] = unhexlify('0701013132333401')

    ac = generateAC(IsoFieldDef.acTags, unhexlify(mk), pan, pan_sn, atc, tags)
    print "ac=", hexlify(ac)

    mk_smi = '1234567890ABCDEF1234567890ABCDEF'
    mk_smc = '1234567890ABCDEF1234567890ABCDEF'
    script = '04DA9F0206123400000000'
    msg = IsoFieldDef.verifyScript(unhexlify(mk_smi), pan, pan_sn, ac, atc, unhexlify(script))



