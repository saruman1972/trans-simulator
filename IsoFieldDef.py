#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import re
from lxml import etree
from pyDes import *
from binascii import *
import EBCDIC
import re
import time
import random
import Configure
import pyDes
from Security import *

class Choices:

    def __init__(self, name):
        self.name = name
        self.elements = []

    def append(self, element):
        self.elements.append(element)


# 字符集
ENC_ASCII = "ASCII"
ENC_EBCDIC = "EBCDIC"

class CharacterSet:

    def encode(self, buffer):
        return buffer

    def decode(self, buffer):
        return buffer

class AsciiCharSet(CharacterSet):

    def encode(self, buffer):
        return buffer

    def decode(self, buffer):
        return buffer

class EbcdicCharSet(CharacterSet):

    def encode(self, buffer):
        return EBCDIC.atoe(buffer)

    def decode(self, buffer):
        return EBCDIC.etoa(buffer)

# static character set available
ASCII_CHAR_SET = AsciiCharSet()
EBCDIC_CHAR_SET = EbcdicCharSet()

# MAC计算模式
class MACField:
    def __init__(self, spec):
        fs = string.split(spec, ':')
        self.index = string.atoi(fs[0])
        if len(fs) == 1:
            self.size = -1      # use field's entire content
        else:
            self.size = string.atoi(fs[1])

class MACFormat:
    def __init__(self):
        self.mac_fields = []

    def setMACFields(self, mac_fields):
        for f in string.split(mac_fields, ' '):
            mf = MACField(f)
            self.mac_fields.append(mf)

    def genMAC(self, transValue):
        macBlock = ''
        for mf in self.mac_fields:
            try:    # for testing purpose, transObj maybe contain some fields that is not included in bitmap
                if mf.size == -1:
                    macBlock = macBlock + transValue[mf.index]['net']
                else:
                    macBlock = macBlock + transValue[mf.index]['net'][:mf.size]
            except:
                pass
        return calcMac(unhexlify(Configure.config['zak']), macBlock)
    def verifyMAC(self, transValue):
        mac = self.genMAC(transValue)
        try:
            if mac == transValue[128]['net']:
                return True
            else:
                return False
        except:
            return False

class MACFormatCUP_Normal(MACFormat):
    def genMAC(self, transValue):
        macBlock = ''
        for mf in self.mac_fields:
            try:    # for testing purpose, transObj maybe contain some fields that is not included in bitmap
                if mf.size == -1:
                    macBlock = macBlock + ' ' + transValue[mf.index]['net']
                else:
                    macBlock = macBlock + ' ' + transValue[mf.index]['net'][:mf.size]
            except:
                pass
        # delete none-printable chars
        macBlock = re.sub("[^0-9a-zA-Z ,\.]", "", macBlock)
        # delete mutiple spaces
        macBlock = re.sub(" +", " ", macBlock)
        # delete the trail space
        macBlock = string.strip(macBlock)
        mac = calcMac(unhexlify(Configure.config['zak']), macBlock)
        return hexlify(mac)

    def verifyMAC(self, transValue):
        mac = self.genMAC(transValue)
        try:
            if mac == transValue[128]['net']:
                return True
            else:
                return False
        except:
            return False

class MACFormatCUP_ChangeKey(MACFormatCUP_Normal):
    def genMAC(self, transValue):
        return MACFormatCUP_Normal.genMAC(self, transValue)

    def genHostMAC(self, transValue):
        mac = MACFormatCUP_Normal.genMAC(self, transValue)
        if transValue[53]['net'][1] == '6':
            zak = transValue[48]['net'][2:]
            key = pyDes.triple_des(zak)
        else:
            zak = transValue[96]['net']
            key = pyDes.des(zak)
        checkValue = key.encrypt("\0\0\0\0\0\0\0\0") 
        return unhexlify(mac) + checkValue[:4]

    def verifyMAC(self, transValue):
        mac = self.genHostMAC(transValue)
        try:
            if mac == transValue[128]['net']:
                return True
            else:
                return False
        except:
            return False


MACFormats = {
    "CUP_NORMAL"    : MACFormatCUP_Normal(),
    "CUP_CHANGEKEY" : MACFormatCUP_ChangeKey()
}

def getMACFormat(fmt):
    fmt = fmt.upper()
    if MACFormats.has_key(fmt):
        return MACFormats[fmt]
    else:
        return None

# 报文格式

class MessageFormatFix:

    def pack(self, bitmap, fields, transValue):
        pan = "0000000000000000"

        data = ""
        for field in fields.fields_array:
            if (field.index <= -1000):    # head
                continue
            elif ((field.index == 64) or (field.index == 128)):
                continue

            (value, tmp_mac_block) = field.isofield.encode(transValue[field.index]['host'])
            transValue[field.index]['net'] = value
            data += value
        return data

    def unpack(self, fielddef, data, transObj):
        indexes = fielddef.fields_index_hash.keys()
        msgDump = ""
        for isofield in fields.fields_array:
            if (isofield.index <= -1000):    # head
                continue

            isofield = fielddef.fields_index_hash[index]
            (value, total_len) = isofield.decode(data)
            if isofield.fieldEnc.visible():
                msgDump += "Field[%3d]:'%s'\n" % (isofield.index, value)
            else:
                msgDump += "Field[%3d]:'%s'\n" % (isofield.index, hexlify(value))
            data = data[total_len:]
            transObj[index] = {'net' : data[0:total_len], 'host' : value}
        return (transObj, msgDump)

class MessageFormat8583(MessageFormatFix):

    def __init__(self):
        self.tlvEncoder = MessageFormatTLV()

    def pack(self, bitmap, fields, transValue, macFormat=None):
        # first deal message type
        (msgtype_str, macBlock) = fields[0].isofield.encode(transValue[0]['host'])
        transValue[0]['net'] = msgtype_str

        # then deal all the fields presented
        data = ""
        indexes = fields.keys()
        indexes.sort()
        hasMac = 0
        for index in indexes:
            if (index <= 0):    # head and message type
                continue
            elif ((index == 64) or (index == 128)):
                hasMac = 1
                continue

            field = fields[index]
            (value, tmp_mac_block) = field.isofield.encode(transValue[index]['host'])
            print value,"|",len(value)
            data += hexlify(value)
            transValue[index]['net'] = value
            macBlock += " " + tmp_mac_block
            if index == 2:
                Configure.config['store_pan'] = transValue[2]['host']
            if index == 23:
                Configure.config['store_pan_sn'] = transValue[23]['host']

        bitmap_str = BitList_to_String(bitmap)
        buf = hexlify(msgtype_str) + hexlify(bitmap_str) + data
        if macFormat != None:
            return unhexlify(buf) + macFormat.genMAC(transValue)
        else:
            return unhexlify(buf)

    def unpack(self, fielddef, data, transObj):
        (value, total_len) = fielddef.fields_index_hash[0].decode(data)
        transObj[0] = {'net' : data[0:total_len], 'host' : value}
        data = data[total_len:]
        msgDump = "Message Type: " + value + "\n"
        bitmap = String_to_BitList(data[:8])
        bitmap_len = 8
        max_field = 64
        if (bitmap[0] == 1):
            bitmap += String_to_BitList(data[8:16])
            bitmap_len = 16
            max_field = 128
        data = data[bitmap_len:]
        for i in range(2, max_field+1):
            if len(data) > 0:
                if (bitmap[i-1] == 1):
                    isofield = fielddef.fields_index_hash[i]
                    if isofield == None:
                        raise NameError, ("--unsupported field[%3d]" % (i))
                    (value, total_len) = isofield.decode(data)
                    if isofield.fieldEnc.visible():
                        if (i == 48) and (transObj[0]['net'] == '0810'):
                            msgDump += "Field[%3d]:'%s'\n" % (isofield.index, hexlify(value))
                        else:
                            msgDump += "Field[%3d]:'%s'\n" % (isofield.index, value)
                    else:
                        msgDump += "Field[%3d]:'%s'\n" % (isofield.index, hexlify(value))
                        if isofield.index == 55:    # IC Data
                            tagObjs = {}
                            (tagObjs, msg) = self.tlvEncoder.unpack(None, value, tagObjs)
                            msgDump += msg + "\n"
                            if tagObjs.has_key('\x91'):   # arpc
                                msgDump += verifyARPC(tagObjs['\x91']) + "\n"
                            if tagObjs.has_key('\x72'):   # issuer script
                                msgDump += processScripts(tagObjs['\x72']) + "\n"
                    transObj[i] = {'net' : data[0:total_len], 'host' : value}
                    data = data[total_len:]
            else:
                transObj[i] = {'net' : '', 'host' : ''}

        keyReset(transObj)
        return (transObj, msgDump)

def packTag(tag, val):
    buf = tag
    if len(val) > 127:
        buf += '\x81'
        buf += chr(len(val))
    else:
        buf += chr(len(val))
    buf += val
    return buf

def unpackTag(buf):
    tag = buf[0]
    buf = buf[1:]
    if ord(tag) & 0x1F == 0x1F:      # 低5位为1，表明tag占用两个字节
        tag += buf[0]
        buf = buf[1:]
    lb = buf[0]
    length = ord(lb)
    buf = buf[1:]
    if length & 0x80:
        ll = length & 0x03
        length = 0
        for i in range(ll):
            lb += buf[i]
            length = length*256 + ord(buf[i])
        buf = buf[ll:]
    val = buf[:length]
    return (tag, lb, val, buf[length:])

class MessageFormatTLV:

    def pack(self, bitmap, fields, transValue):
        buf = ""
        for tagDef in fields.fields_array:
            if transValue.has_key(tagDef.tag) and len(transValue[tagDef.tag]) > 0:
                buf += packTag(tagDef.tag, transValue[tagDef.tag])
        return buf

    def unpack(self, fielddef, data, tagObjs):
        msgDump = ""
        while len(data)>0:
            (tag, lb, val, data) = unpackTag(data)
            tagObjs[tag] = val
            msgDump += "  Tag[" + hexlify(tag) + "]"
            if len(tag) == 1:
                msgDump += "  "
            msgDump += ": " + hexlify(lb) + " " + hexlify(val) + "\n"
        return (tagObjs, msgDump)

def verifyARPC(tag91):
    if (tag91 == None):
        return "No ARPC in response\n"
    if (len(tag91) != 10):
        return "invalid ARPC length\n"
    mk = Configure.config['mk_ac']
    arpc = tag91[:8]
    resp_cd = tag91[8:]
    print "mk=",mk
    print "store_pan=",hexlify(Configure.config['store_pan'])
    print "store_pan_sn=",hexlify(Configure.config['store_pan_sn'])
    print "store_atc=",hexlify(Configure.config['store_atc'])
    print "store_ac=",hexlify(Configure.config['store_ac'])
    m = generateARPC(unhexlify(mk), Configure.config['store_pan'], Configure.config['store_pan_sn'], Configure.config['store_atc'], Configure.config['store_ac'], resp_cd)
    if m == arpc:
        return "ARPC verify success\n"
    else:
        return "ARPC verify failed\n"

def processScripts(scripts):
    msgDump = ""
    while len(scripts)>0:
        (tag, lb, val, scripts) = unpackTag(scripts)
        msgDump += processScript(val)
    return msgDump

def processScript(script):
    mk_smi = Configure.config['mk_smi']
    return verifyScript(unhexlify(mk_smi), Configure.config['store_pan'], Configure.config['store_pan_sn'], Configure.config['store_ac'], Configure.config['store_atc'], script)



def verifyScript(mk_smi, pan, pan_sn, ac, atc, script):
    (cla, ins, p1, p2, lc, data, mac) = unpackScript(script)
    msg = "Script:\n"
    msg += "  CLA  : " + hexlify(cla) + "\n"
    msg += "  INS  : " + hexlify(ins) + "\n"
    msg += "  P1   : " + hexlify(p1) + "\n"
    msg += "  P2   : " + hexlify(p2) + "\n"
    msg += "  Lc   : " + hexlify(lc) + "\n"
    msg += "  Data : " + hexlify(data) + "\n"
    msg += "  MAC  : " + hexlify(mac) + "\n"
    msg += "================================================\n"
    m = generateScriptMAC(mk_smi, pan, pan_sn, ac, atc, cla, ins, p1, p2, lc, data)
    if m == mac:
        msg += "mac verify success!\n"
    else:
        msg += "mac verify failed!\n"
    return msg


def keyReset(transObj):
    if transObj[0]['host'] == '0810' and transObj[39]['host'] == '00':
        # key reset
        print transObj
        if transObj[70]['host'] == '101':
            zmk = Configure.config['zmk']
            k = pyDes.triple_des(unhexlify(zmk))
            if transObj[53]['net'][1] == '6': # double length
                new_key = hexlify(k.decrypt(transObj[48]['host']))
            else:
                new_key = hexlify(k.decrypt(transObj[96]['host']))
            if transObj[53]['net'][0] == '1':
                Configure.config['zpk'] = new_key
            else:
                Configure.config['zak'] = new_key




MESSAGE_FORMAT_FIX = MessageFormatFix()
MESSAGE_FORMAT_8583 = MessageFormat8583()

# predefined justification value
NO_JUST = 0
LEFT_JUST = 1
RIGHT_JUST = 2

# 域编码格式（A AN N ANS BCD....）
class FieldEncode:

    def __init__(self, regularExpression=None):
        self.re = regularExpression

    def encode(self, variable, size, charSet, padding):
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet):
        return (charSet.decode(buffer), size)

    def valid(self, variable):
        """ valid the content in variables according to the predifined pattern """
        if (self.re == None):
            return True
        elif (self.re.match(variable) == None):
            return False
        else:
            return True

    def padding(self, variable, size, align, pad_char):
        padding = pad_char * (size - len(variable))
        if (align == LEFT_JUST):
            return variable+padding
        elif (align == RIGHT_JUST):
            return padding+variable

    def visible(self):
        """ if the value in the field is visible """
        return True

    def length(self, size):
        """ return the packed field length """
        return size

    def dopadding(self, variable, size):
        return variable

    def toAscii(self, variable):
        return variable
    
class FieldEncode_A(FieldEncode):
    """ alphabetical characters """
    def __init__(self):
        regularExpression = re.compile('^[a-zA-Z]*$')
        FieldEncode.__init__(self, regularExpression)

    def toAscii(self, variable):
        return variable.encode("GBK")
    
    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        var = var.decode("GBK")
        return (charSet.decode(var), size)

    def length(self, size):
        return self.size

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_N(FieldEncode):
    """ numeric digits """
    def __init__(self):
        regularExpression = re.compile('^[0-9]*$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, RIGHT_JUST, '0')

class FieldEncode_S(FieldEncode):
    """ special characters """
    def __init__(self):
        regularExpression = re.compile('^\s*$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_AN(FieldEncode):
    """ alphabetical and numeric characters """
    def __init__(self):
        regularExpression = re.compile('^[0-9a-zA-Z]*$')
        FieldEncode.__init__(self, regularExpression)

    def toAscii(self, variable):
        return variable.encode("GBK")
    
    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        var = var.decode("GBK")
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_AS(FieldEncode):
    """ alphabetical and special characters """
    def __init__(self):
        regularExpression = re.compile('^[a-zA-Z\s]*$')
        FieldEncode.__init__(self, regularExpression)

    def toAscii(self, variable):
        return variable.encode("GBK")
    
    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        var = var.decode("GBK")
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_NS(FieldEncode):
    """ numeric and special characters """
    def __init__(self):
        regularExpression = re.compile('^[0-9\s]*$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_ANS(FieldEncode):
    """ alphabetical, numeric and special characters """
    def __init__(self):
        regularExpression = re.compile('^[0-9a-zA-Z]*\s$')
        FieldEncode.__init__(self, regularExpression)

    def toAscii(self, variable):
        return variable.encode("GBK")
    
    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        var = var.decode("GBK")
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

class FieldEncode_L(FieldEncode):
    """ Length """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        variable = string.atoi(variable)
        value = ''
        for i in range(size):
            value = chr(variable & 0xff) + value
            variable = variable << 8
        return value

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        val = 0
        for i in range(size):
            val = (val << 8) + ord(var[i])
        return ("%d" % val, size)

class FieldEncode_B(FieldEncode):
    """ Binary """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = variable[:size]
        return variable

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (var, size)

    def visible(self):
        return False

class FieldEncode_BHX(FieldEncode):
    """ Binary, hex """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = variable[:self.length(size)]
        return hexlify(variable).upper()

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (unhexlify(var), size)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def visible(self):
        return False

class FieldEncode_X(FieldEncode):
    """ (C=credit/D=debit) + numeric """
    def __init__(self):
        regularExpression = re.compile('^(C|D)[0-9]*\s$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            sign = variable[:1]
            value = variable[1:size]
            value = self.padding(value, size-1, RIGHT_JUST, '0')
            variable = sign + value
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (charSet.decode(var), size)

class FieldEncode_BCD(FieldEncode):
    """ Packed decimal, BCD nybbles """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        if (len(variable) % 2):    # 奇数长度位，在最后补'F'
            variable += 'F'
        return unhexlify(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        nbytes = (size+1)/2
        var = buffer[:nbytes]
        var = hexlify(var)
        if (size % 2):    # 去掉最后补的'F'
            var = var[:-1]
        return (var, nbytes)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, RIGHT_JUST, '0')

class FieldEncode_BCX(FieldEncode):
    """ Packed X data """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        sign = charSet.encode(variable[:1])
        value = variable[1:]
        if (padding):
            variable = self.dopadding(variable, size)
        if (len(value) % 2):    # 奇数长度位，在最后补'F'
            value += 'F'
        return sign + unhexlify(value)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        nbytes = (size+1)/2
        sign = buffer[:1]
        var = buffer[1:nbytes]
        var = hexlify(var)
        if ((size-1) % 2):    # 去掉最后补的'F'
            var = var[:-1]
        return (sign + var, nbytes)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size-1, RIGHT_JUST, '0')

class FieldEncode_BC0(FieldEncode):
    """ Packed decimal, BCD nybbles, 0 pad left """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        if (len(variable) % 2):    # 奇数长度位，在最前面补'0'
            variable = '0' + variable
        return unhexlify(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        nbytes = (size+1)/2
        var = buffer[:nbytes]
        var = hexlify(var)
        if (size % 2):        # 奇数长度，去掉最前面补的'0'
            var = var[1:]
        return (var, nbytes)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, RIGHT_JUST, '0')

class FieldEncode_BCZ(FieldEncode):
    """ track data in BCD format, Packed decimal, BCD nybbles, no padding"""
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        # 首先将所有的非数字替换成'd'
        variable = re.sub('[^0-9]', 'd', variable)
        # continue encoding
        if (padding):
            variable = self.dopadding(variable, size)
        if (len(variable) % 2):    # 奇数长度位，在最后补'F'
            variable += 'F'
        return unhexlify(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        nbytes = (size+1)/2
        var = buffer[:nbytes]
        var = hexlify(var)
        # 将所有的'd'替换成'='
        variable = re.sub('d', '=', variable)
        if (size % 2):    # 去掉最后补的'F'
            var = var[:-1]
        return (var, nbytes)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, RIGHT_JUST, '0')

class FieldEncode_BZ0(FieldEncode):
    """ track data in BCD format, 0 pad left """
    def __init__(self):
        FieldEncode.__init__(self)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        # 首先将所有的非数字替换成'd'
        variable = re.sub('[^0-9]', 'd', variable)
        # continue encoding
        if (padding):
            variable = self.dopadding(variable, size)
        if (len(variable) % 2):    # 奇数长度位，在最前面补'0'
            variable = '0' + variable
        return unhexlify(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        nbytes = (size+1)/2
        var = buffer[:nbytes]
        var = hexlify(var)
        # 将所有的'd'替换成'='
        var = re.sub('d', '=', var)
        if (size % 2):        # 奇数长度，去掉最前面补的'0'
            var = var[1:]
        return (var, nbytes)

    def length(self, size):
        if size % 2:
            return size/2 + 1
        else:
            return size/2

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, RIGHT_JUST, '0')

class FieldEncode_Z(FieldEncode):
    """ track data """
    def __init__(self):
        regularExpression = re.compile('^[0-9=]*$')
        FieldEncode.__init__(self, regularExpression)

    def encode(self, variable, size, charSet=ASCII_CHAR_SET, padding=False):
        if (padding):
            variable = self.dopadding(variable, size)
        return charSet.encode(variable)

    def decode(self, buffer, size, charSet=ASCII_CHAR_SET):
        var = buffer[:size]
        return (charSet.decode(var), size)

    def dopadding(self, variable, size):
        variable = variable[:size]
        return self.padding(variable, size, LEFT_JUST, ' ')

# predefined field encoder
fieldEncodeMap = {
                    "FE_A"    : FieldEncode_A(),
                    "FE_N"    : FieldEncode_N(),
                    "FE_S"    : FieldEncode_S(),
                    "FE_AN"   : FieldEncode_AN(),
                    "FE_AS"   : FieldEncode_AS(),
                    "FE_NS"   : FieldEncode_NS(),
                    "FE_ANS"  : FieldEncode_ANS(),
                    "FE_L"    : FieldEncode_L(),
                    "FE_B"    : FieldEncode_B(),
                    "FE_BHX"  : FieldEncode_BHX(),
                    "FE_X"    : FieldEncode_X(),
                    "FE_BCD"  : FieldEncode_BCD(),
                    "FE_BCX"  : FieldEncode_BCX(),
                    "FE_BC0"  : FieldEncode_BC0(),
                    "FE_BCZ"  : FieldEncode_BCZ(),
                    "FE_BZ0"  : FieldEncode_BZ0(),
                    "FE_Z"    : FieldEncode_Z() }


# 域类型（固定长度、2位变长....）

class FieldType:

    def __init__(self):
        pass

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        return ""

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        """ 返回值：（变长域长度占几个字节，变长域内容长度）"""
        return (0,0)

    def varLength(self):
        return False

class FieldType_FIXED(FieldType):
    """ Fixed Length field """

    def encode(self, variable, size, charSet=ASCII_CHAR_SET):
        return ""

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        return (0, 0)

class FieldType_LLFIX(FieldType):
    """ Fixed Length field, 2 length count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 99):
            raise ValueError(" %d is too long " % len)
        len_str = "%02d" % len
        return charSet.encode(len_str)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        len_str = charSet.decode(buffer[:2])
        var_len = string.atoi(len_str)
        return (2, var_len)

class FieldType_LLLFIX(FieldType):
    """ Fixed Length field, 3 length count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 999):
            raise ValueError(" %d is too long " % len)
        len_str = "%03d" % len
        return charSet.encode(len_str)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        len_str = charSet.decode(buffer[:3])
        var_len = string.atoi(len_str)
        return (3, var_len)

class FieldType_LLVAR(FieldType):
    """ Variable Length field, 2 length count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 99):
            raise ValueError(" %d is too long " % len)
        len_str = "%02d" % len
        return charSet.encode(len_str)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        len_str = charSet.decode(buffer[:2])
        var_len = string.atoi(len_str)
        return (2, var_len)

    def varLength(self):
        return True

class FieldType_LLLVAR(FieldType):
    """ Variable Length field, 3 length count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 999):
            raise ValueError(" %d is too long " % len)
        len_str = "%03d" % len
        return charSet.encode(len_str)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        len_str = charSet.decode(buffer[:3])
        var_len = string.atoi(len_str)
        return (3, var_len)

    def varLength(self):
        return True

class FieldType_V1VAR(FieldType):
    """ Variable Length field, binary BCD digit count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 255):
            raise ValueError("%d is too long" % len)
        return chr(len)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        var_len = ord(buffer[0])
        return (1, var_len)

    def varLength(self):
        return True

class FieldType_V2VAR(FieldType):
    """ Variable Length field, binary BCD byte count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 255):
            raise ValueError("%d is too long" % len)
        return chr(len)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        var_len = ord(buffer[0])
        return (1, var_len)

    def varLength(self):
        return True

class FieldType_V3VAR(FieldType):
    """ Variable Length field, binary BCD byte count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 65535):
            raise ValueError("%d is too long" % len)
        high_byte = len / 256
        low_byte = len % 256
        return chr(high_byte) + chr(low_byte)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        var_len = ord(buffer[0])*256 + ord(buffer[1])
        return (2, var_len)

    def varLength(self):
        return True

class FieldType_BCD2VAR(FieldType):
    """ Variable Length field, binary BCD count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 99):
            raise ValueError("%d is too long" % len)
        return unhexlify("%02d" % len)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        var_len = string.atoi(hexlify(buffer[0]))
        return (1, var_len)

    def varLength(self):
        return True

class FieldType_BCD3VAR(FieldType):
    """ Variable Length field, binary BCD count """

    def encodeLength(self, len, charSet=ASCII_CHAR_SET):
        if (len > 999):
            raise ValueError("%d is too long" % len)
        return unhexlify("%04d" % len)

    def decodeLength(self, buffer, charSet=ASCII_CHAR_SET):
        var_len = string.atoi(hexlify(buffer[:2]))
        return (2, var_len)

    def varLength(self):
        return True


# predefined field types
fieldTypeMap = {
                "FT_FIXED"   : FieldType_FIXED(),
                "FT_LLFIX"   : FieldType_LLFIX(),
                "FT_LLLFIX"  : FieldType_LLLFIX(),
                "FT_LLVAR"   : FieldType_LLVAR(),
                "FT_LLLVAR"  : FieldType_LLLVAR(),
                "FT_V1VAR"   : FieldType_V1VAR(),
                "FT_V2VAR"   : FieldType_V2VAR(),
                "FT_V3VAR"   : FieldType_V3VAR(),
                "FT_BCD2VAR" : FieldType_BCD2VAR(),
                "FT_BCD3VAR" : FieldType_BCD3VAR()}



class ValueOrigin:

    USER = 1

    def __init__(self):
        self.type = None

    def getValue(self, user_input, transObj):
        """ 当页面录入完成之后用于生成具体的值 """
        return user_input

    def setValue(self, value, transObj):
        """ 当收到返回信息等时候设置到该页面控件中 """
        return value

class ValueOriginFixvalue(ValueOrigin):

    def __init__(self, fixvalue):
        ValueOrigin.__init__(self)
        self.fixvalue = fixvalue

    def getValue(self, user_input, transObj):
        return self.fixvalue

    def setValue(self, value, transObj):
        return self.fixvalue

class ValueOriginUser(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)
        self.type = ValueOrigin.USER

    def getValue(self, user_input, transObj):
        return user_input

class ValueOriginDateTime(ValueOrigin):

    def __init__(self, format):
        ValueOrigin.__init__(self)
        self.format = format

    def getValue(self, user_input, transObj):
        return time.strftime(self.format)

class ValueOriginSeqNo(ValueOrigin):

    def __init__(self, length, startVal):
        ValueOrigin.__init__(self)
        self.length = length
        self.seqNo = startVal

    def getValue(self, user_input, transObj):
        self.seqNo += 1
        return "%0*.*d" % (self.length, self.length, self.seqNo)

class ValueOriginResponseCode(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        return "00"

class ValueOriginAuthorizationCode(ValueOrigin):

    def __init__(self, length):
        ValueOrigin.__init__(self)
        self.rand = random.Random()
        self.length = length
        self.upper_bound = 10**length

    def getValue(self, user_input, transObj):
        return "%0*.*d" % (self.length, self.length, self.rand.randint(0, self.upper_bound))

class ValueOriginPIN(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        pin = user_input
        if transObj.has_key(2):
            pan = transObj[2]['host']
        else:
            pan = '0'*16
        zpk = Configure.config['zpk']
        pinblock_mode = Configure.config['pinblock_mode']
        if (len(zpk) > 16):
            key = pyDes.triple_des(unhexlify(zpk))
        else:
            key = pyDes.des(unhexlify(zpk))
        # field 2 is card no
        if (pinblock_mode == "01"):
            pass
        elif (pinblock_mode == "08"):
            pan = '0000000000000000'
        else:
            # 其他情况，暂时按照"08"处理
            pan = '0000000000000000'
        pinblock = makePinBlock(pan, pin)
        print "getValue:pan=", pan, "pinblock=", hexlify(pinblock), "zpk=", zpk
        return key.encrypt(pinblock)

    def setValue(self, value, transObj):
        if transObj.has_key(2):
            pan = transObj[2]['host']
        else:
            pan = '0'*16
        zpk = Configure.config['zpk']
        pinblock_mode = Configure.config['pinblock_mode']
        if (len(zpk) > 16):
            key = pyDes.triple_des(unhexlify(zpk))
        else:
            key = pyDes.des(unhexlify(zpk))
        pinblock = key.decrypt(value)
        # field 2 is card no
        if (pinblock_mode == "01"):
            pass
        elif (pinblock_mode == "08"):
            pan = '0000000000000000'
        else:
            # 其他情况，暂时按照"08"处理
            pan = '0000000000000000'
        pin = extractPIN(pan, pinblock)
        return pin

class ValueOriginSecurityInfo(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        if len(user_input) > 0:
            return user_input
        else:
            pinblock_mode = Configure.config['pinblock_mode']
            if len(Configure.config['zpk']) <= 16: # single length
                if (pinblock_mode == "08"):
                    return "1000000000000000"
                else:
                    return "2000000000000000"
            else:
                if (pinblock_mode == "08"):
                    return "1600000000000000"
                else:
                    return "2600000000000000"

class ValueOriginMAC(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        mac = calcMac(unhexlify(Configure.config['zak']), macBlock)
        return mac

class ValueOriginChoices(ValueOrigin):

    def __init__(self, choices):
        ValueOrigin.__init__(self)
        self.choices = choices

    def getValue(self, user_input, transObj):
        return user_input

class ValueOriginResponseCode(ValueOrigin):

    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        return "00"

class ValueOriginPackageLength(ValueOrigin):
    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
#        (header, body) = info
#        return "%d" % len(body)
        return user_input

class ValueOriginBlockLength(ValueOrigin):
    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
#        (header, body) = info
#        return "%d" % header.blockLength()
        return user_input

class ValueOriginBodyLength(ValueOrigin):
    def __init__(self):
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
#        (header, body) = info
#        return "%d" % len(body)
        return user_input

class ValueOriginCopyFrom(ValueOrigin):
    def __init__(self, index):
        self.index = index
        ValueOrigin.__init__(self)

    def getValue(self, user_input, transObj):
        return transObj[self.index]['host']

class ValueOriginICData(ValueOrigin):
    def __init__(self, fields, acTags, packTags):
        ValueOrigin.__init__(self)
        self.fields = fields
        self.acTags = acTags
        self.packTags = packTags
        self.packFields = FieldsDef()
        for tag in packTags:
            self.packFields.addField(fields.fields_tag_hash[tag])

    def getValue(self, user_input, transObj):
        tagObj = {}
        for field in self.fields.fields_array:
            (val, dummy) = field.encode(field.valueOrigin.getValue('', transObj))
            tagObj[field.tag] = val
        mk = Configure.config['mk_ac']
        pan = transObj[2]['host']
        pan_sn = transObj[23]['host']
        atc = tagObj['\x9F\x36']
        Configure.config['store_atc'] = atc
        arqc = generateAC(self.acTags, unhexlify(mk), pan, pan_sn, atc, tagObj)
        tagObj['\x9F\x26'] = arqc
        Configure.config['store_ac'] = arqc

        # testing script
        mk_smi = Configure.config['mk_smi']
        cla = '\x04'
        ins = '\xDA'
        p1 = '\x9F'
        p2 = '\x56'
        lc = chr(2 + 4)
        data = '\x12\x34'
        mac = generateScriptMAC(unhexlify(mk_smi), pan, pan_sn, arqc, atc, cla, ins, p1, p2, lc, data)
        script = cla + ins + p1 + p2 + lc + data + mac
        tagObj['\x72'] = packTag('\x86', script) + packTag('\x86', script)
        # testing arpc
        resp_cd = "00"
        arpc = generateARPC(unhexlify(mk), pan, pan_sn, atc, arqc, resp_cd)
        tagObj['\x91'] = arpc + resp_cd

        buf = self.fields.messageFormat.pack('', self.packFields, tagObj)
        return buf

acTags = ['\x9F\x02', # | '9F02' | 6 | n12    | terminal | amount, authorized                    |
          '\x9F\x03', # | '9F03' | 6 | n12    | terminal | amount, other(binary)                 |
          '\x9F\x1A', # | '9F1A' | 2 | cn3    | terminal | terminal country code                 |
          '\x95',     # | '95'   | 5 | b      | terminal | terminal verification result(TVR)     |
          '\x5F\x2A', # | '5F2A' | 2 | cn3    | terminal | transaction currency code             |
          '\x9A',     # | '9A'   | 3 | cn6    | terminal | transaction date                      |
          '\x9C',     # | '9C'   | 1 | cn2    | terminal | transaction type                      |
          '\x9F\x37', # | '9F37' | 2 | b      | terminal | unpredictable number                  |
          '\x82',     # | '82'   | 2 | b      | ICC      | application interactive property(AIP) |
          '\x9F\x36', # | '9F36' | 2 | b      | ICC      | application transaction counter(ATC)  |
          '\x9F\x10'] # | '9F34' | 4 | b      | ICC      | card verification result(CVR)         |


VALUE_ORIGIN_USER = ValueOriginUser()





# 数据域定义
class DataField:
    """ field definition """

    FT_NULL = "FT_NULL"

    def __init__(self, charSet=ASCII_CHAR_SET):
        self.index = -1                        # 域8583的编号
        self.name = ""                        # 域的名称
        self.desc = ""                        # 域描述
        self.fieldEnc = None                # 域打包、解包时候的类型（FE_N FE_AN FE_ANS等）
        self.fieldType = None                # 域长度类型（FIXED LLVAR LLLVAR等）
        self.size = 0                        # 该域的大小
        self.disp_size = 0                    # 该域用于显示时候的大小
        self.cal_mac = 0                    # 该域是否参与计算mac
        self.cal_mac_size = 0                # 该域参与计算mac的长度
        self.sub_fields = None                # 域包含的子域定义数组（关联数组）
        self.charSet = charSet                # 域编码格式（ascii ebcdic）
        self.valueOrigin = VALUE_ORIGIN_USER    # 域取值类型（系统产生、用户输入等）
        self.tag = ""                           # TLV格式，标签

    def padding(self, variable):
        return self.fieldEnc.dopadding(variable, self.size)

    def encode(self, variable):
        """ return value: (packed_data, mac_block) """
        print "index=", self.index
        variable = self.fieldEnc.toAscii(variable)
        var_len = len(variable)
        print "encode var len=", var_len
        lenstr = self.fieldType.encodeLength(var_len, self.charSet)
        if not self.fieldType.varLength():  # 固定长度，需要padding
            var = self.fieldEnc.encode(variable, self.size, self.charSet, padding=True)
        else:
            var = self.fieldEnc.encode(variable, self.size, self.charSet, padding=False)
        packed_data = lenstr + var
        if (self.cal_mac):
            mac_block = packed_data[:self.cal_mac_size]
        else:
            mac_block = ""

        return (packed_data, mac_block)

    def decode(self, data, decodeLength=True):
        """ return value: (var, total_len) """

        if decodeLength:
            (len_len, var_len) = self.fieldType.decodeLength(data, self.charSet)
        else:
            len_len = 0

        if self.fieldType.varLength():  # 变长域
            data = data[len_len:]
        else:
            var_len = self.size
        (var,nbytes) = self.fieldEnc.decode(data, var_len, self.charSet)

        return (var, len_len+nbytes)

    def length(self):
        return self.fieldEnc.length(self.size)

# 数据域集合定义
class FieldsDef:

    def __init__(self):
        self.name = ""
        self.fields_name_hash = {}
        self.fields_index_hash = {}
        self.fields_tag_hash = {}
        self.fields_array = []
        self.choices_hash = {}
        self.header_fields_hash = {}
        self.messageFormat = MESSAGE_FORMAT_FIX
        self.mac_fields = ""

    def addField(self, field):
        self.fields_index_hash[field.index] = field
        self.fields_name_hash[field.name] = field
        self.fields_tag_hash[field.tag] = field
        self.fields_array.append(field)

    def getFieldsArray(self):
        return self.fields_array

    def getFieldsIndexHash(self):
        return self.fields_index_hash

    def getFieldsNameHash(self):
        return self.fields_name_hash

    def addChoices(self, choices):
        self.choices_hash[choices.name] = choices

    def getChoices(self, name):
        return self.choices_hash[name]


# 读取域定义文件的分析器
def LoadCalcValue(field, elem):
    if (elem.attrib['type'] == "DATE_TIME"):
        return ValueOriginDateTime(elem.attrib['format'])
    elif (elem.attrib['type'] == "SEQ_NO"):
        try:
            start_val = string.atoi(elem.attrib['start_val'])
        except:
            start_val = 0
        return ValueOriginSeqNo(field.size, start_val)
    elif (elem.attrib['type'] == "PIN"):
        return ValueOriginPIN()
    elif (elem.attrib['type'] == "SECURITY_INFO"):
        return ValueOriginSecurityInfo()
    elif (elem.attrib['type'] == "AUTHORIZATION_CODE"):
        return ValueOriginAuthorizationCode(6)
    elif (elem.attrib['type'] == "RESPONSE_CODE"):
        return ValueOriginResponseCode()
    elif (elem.attrib['type'] == "LENGTH"):
        if (elem.attrib['input'] == "PACKAGE"):
            return ValueOriginPackageLength()
        elif (elem.attrib['input'] == "BLOCK"):
            return ValueOriginBlockLength()
        elif (elem.attrib['input'] == "BODY"):
            return ValueOriginBodyLength()
    elif (elem.attrib['type'] == "IC_DATA"):
        acTags = map(unhexlify, elem.attrib['ac_tags'].split(','))
        packTags = map(unhexlify, elem.attrib['pack_tags'].split(','))
        sub_name = elem.attrib['sub_type']
        return ValueOriginICData(field.sub_fields[sub_name], acTags, packTags)
    elif (elem.attrib['type'] == "COPY"):
        return ValueOriginCopyFrom(string.atoi(elem.attrib['index']))
    else:
        raise ValueError('invalid calculate type [' + elem.attrib['type'] + ']')

def LoadField(charSet, dicts, elem):
    field = DataField(charSet)
    for e in elem:
        if e.tag == 'name':
            field.name = e.text.strip()
        elif e.tag == 'index':
            field.index = string.atoi(e.text.strip())
        elif e.tag == 'description':
            field.desc = e.text.strip()
        elif e.tag == 'field_encode':
            try:
                field.fieldEnc = fieldEncodeMap[e.text.strip()]
            except:
                raise ValueError("invalid field_encode[%s]" % e.text)
        elif e.tag == 'field_type':
            try:
                field.fieldType = fieldTypeMap[e.text.strip()]
            except:
                raise ValueError("invalid field_type[%s]" % e.text)
        elif e.tag == 'size':
            field.size = string.atoi(e.text.strip())
        elif e.tag == 'tag':    # ic tag
            field.tag = unhexlify(e.text.strip())
        elif e.tag == 'value':
            e = e[0]
            if e.tag == 'choices':
                choices = dicts[e.attrib['name']]
                field.valueOrigin = ValueOriginChoices(choices)
            elif e.tag == 'calculate':
                field.valueOrigin = LoadCalcValue(field, e)
        elif e.tag == 'fixvalue':
            fixvalue = e.attrib['value']
            field.valueOrigin = ValueOriginFixvalue(fixvalue)
        elif e.tag == 'sub_fields':
            field.sub_fields = {}
            for t in e.xpath('sub_field_type'):
                # 定义该域的一个子域组合类型
                fieldsDef = FieldsDef()
                try:
                    fieldsDef.name = t.attrib['name']
                except:
                    fieldsDef.name = "Anonymous"
                if t.attrib.has_key('format'):
                    if t.attrib['format'] == 'TLV':
                        fieldsDef.messageFormat = MessageFormatTLV()
                for f in t.xpath('sub_field'):
                    fieldsDef.addField(LoadField(charSet, dicts, f))
                field.sub_fields[fieldsDef.name] = fieldsDef

    return field

def LoadIsoFieldDef(filename, dicts=None):
    fieldsDef = FieldsDef()
    doc = etree.parse(filename)
    root = doc.getroot()

    try:
        char_set = root.attrib['char_set']
        char_set = char_set.lower()
        if (char_set == "ascii"):
            charSet = ASCII_CHAR_SET
        elif (char_set == "ebcdic"):
            charSet = EBCDIC_CHAR_SET
        else:
            charSet = ASCII_CHAR_SET
    except:
        charSet = ASCII_CHAR_SET

    try:
        message_format = root.attrib['message_format']
        message_format = message_format.lower()
        if (message_format == "fix"):
            fieldsDef.messageFormat = MESSAGE_FORMAT_FIX
        else:
            fieldsDef.messageFormat = MESSAGE_FORMAT_8583
    except:
        fieldsDef.messageFormat = MESSAGE_FORMAT_8583

    try:
        fieldsDef.mac_fields = root.attrib['mac_fields']
    except:
        fieldsDef.mac_fields = ""

    for elem in doc.xpath('/field_def/field'):
        field = LoadField(charSet, dicts, elem)
        fieldsDef.addField(field)

    return fieldsDef

# the global IsoFieldDef variable
GlobalIsoFieldDef = None

if (__name__ == "__main__"):
    encoder = MessageFormatTLV()
    tagObjs = {}
    msg = "950501020304059F0281820000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    (dummy, dump_msg) = encoder.unpack(None, unhexlify(msg), tagObjs)
    print dump_msg

    from Dictionary import LoadDictionaries
#    fielddef = LoadIsoFieldDef("project/jcb/JcbFieldDef.xml", None)
    dicts = LoadDictionaries("project/bos2.1/dictionary")
    fielddef = LoadIsoFieldDef("project/bos2.1/Bos21FieldDef.xml", dicts)
    fields = fielddef.getFieldsIndexHash()
    for k in fields.keys():
        f = fields[k]
        print "index=%d,desc=%s,field_charset=%s,field_encode=%s,field_type=%s,size=%d" % (f.index, f.desc, f.charSet, f.fieldEnc, f.fieldType, f.size)

