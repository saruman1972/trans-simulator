#!/usr/bin/python
# -*- coding: gbk -*-

from lxml import etree
import string
from binascii import *
import time
import pyDes
import re
from IsoFieldDef import *
import wx
from Security import *
from ListFile import listFiles
import IsoFieldDef
from Utility import *

class VariableField:

    ASC = 0
    BCD = 1
    HEX = 2

    ASCII = 0
    NUMBER = 1

    def __init__(self, transDesc, isofield):
        self.transDesc = transDesc
        self.isofield = isofield
        if (isofield != None):
            self.size = isofield.size
        else:
            self.size = 0
        self.show = 0
        self.value = ""
        self.copy_field_maps = []
        self.copy_field_type = ""

    def getValue(self, transObj):
        return self.isofield.valueOrigin.getValue(self.value, transObj)

def MakeField(transDesc, elem):
    if elem.attrib.has_key('index'):
        index = string.atoi(elem.attrib['index'])
#        assert(index >= 0)
        try:
            isofield = transDesc._fielddef.fields_index_hash[index]
        except:
            raise ValueError("field index out of range [%d]" % index)
        var = VariableField(transDesc, isofield)
    elif elem.attrib.has_key('name'):
        try:
            isofield = transDesc._fielddef.fields_name_hash[elem.attrib['name']]
        except:
            raise ValueError("field name [" + elem.attrib['name'] + "] does'nt exist")
        index = isofield.index
        var = VariableField(transDesc, isofield)
    else:
        raise ValueError("field should has a index or name")

    if (index > transDesc._maxField):
        transDesc._maxField = index
    if (index > 1) :
        transDesc._bitmap[index-1] = 1
    transDesc._fields[index] = var

    try:
        var.show = string.atoi(elem.attrib["show"])
    except:
        pass
    try:
        var.value = decodeXMLString(elem.attrib["value"]).encode("gbk")
    except:
        pass
    try:
        var.size = string.atoi(elem.attrib["size"])
    except:
        pass

    try:
        var.subfield_type = decodeXMLString(elem.attrib["subfield_type"])
    except:
        pass

    cf = elem.xpath('copy_field')
    if len(cf) > 0:
        cf = cf[0]
        if cf.attrib.has_key('type'):
            var.copy_field_type = cf.attrib['type']

        for f in cf.xpath('field_map'):
            of = f.xpath('original_field')[0]
            original_index = string.atoi(of.attrib['index'])
            if of.attrib.has_key('type'):
                original_type = of.attrib['type']
            else:
                original_type = 'Request'
            try:
                tf = f.xpath('target_field')[0]
                target_name = tf.attrib['name']
            except:
                target_name = ''
            var.copy_field_maps.append((original_type, original_index, target_name))

#        if attrs.has_key('keyfields'):
#            keyfields = attrs['keyfields'].split(' ')
#            keyfields.sort()
#            for i in range(len(keyfields)):
#                keyfields[i] = string.atoi(keyfields[i])
#            self._transDesc.keyfields = keyfields
#        if attrs.has_key('keyvalue'):
#            self._transDesc.keyvalue = attrs['keyvalue']

    return var


def CreateTransDescObject(fielddef, filename, config):
    """ create a transaction description object from file """

    #    wx.MessageDialog(None, "读取文件["+filename+"]出错", style=wx.ICON_ERROR)
    doc = etree.parse(filename)
    root = doc.getroot()

    if root.tag == 'package_header':
        transDesc = Package(fielddef, config)
    else:
        transDesc = TransactionDesc(fielddef, config)
    try:
        transDesc.name = root.attrib['name']
    except:
        transDesc.name = ""

    try:
        transDesc.desc = decodeXMLString(root.attrib['desc'])
    except:
        transDesc.desc = ""

    if root.attrib.has_key('mac_format'):
        transDesc._macFormat = IsoFieldDef.getMACFormat(root.attrib['mac_format'])
#        if root.attrib.has_key('mac_fields') != True:
#            raise ValueError('invalid mac_format [' + root.attrib['mac_format'] + ']')
#        transDesc._macFormat.setMACFields(root.attrib['mac_fields'])
        if root.attrib.has_key('mac_fields'):
            transDesc._macFormat.setMACFields(root.attrib['mac_fields'])
        else:
            transDesc._macFormat.setMACFields(fielddef.mac_fields)

    headLen = 0
    for elem in root.xpath('field'):
        var = MakeField(transDesc, elem)

        if root.tag == 'package_header':
            headLen += var.isofield.length()
            if var.isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginBlockLength:
                headLenVar = var
                headLenVar.value = "%d" % headLen
            elif var.isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginBodyLength:
                transDesc._bodyLenField = var
            elif var.isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginPackageLength:
                transDesc._packageLenField = var


    if root.tag == "iso8583":
        if (transDesc._maxField > 64):
            transDesc._bitmap[0] = 1
        else:
            transDesc._bitmap = transDesc._bitmap[:64]

    return transDesc

def LoadTransactions(path, fielddef, config):
    transDescs = []
    cases = listFiles(path, '*.xml', recurse=0)
    for case in cases:
        transDesc = CreateTransDescObject(fielddef, case, config)
        transDescs.append(transDesc)
    return transDescs


class TransactionDesc:

    def __init__(self, fielddef, config):
        self._fielddef = fielddef;
        self._config = config;
        self._bitmap = [0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0,0,0,
                        0,0,0,0,0,0,0,0]            # 128 fields
        self._fields = {}
        self._maxField = 0
        self._macFormat = None

    def pack(self, transValue):
        buf = self._fielddef.messageFormat.pack(self._bitmap[:], self._fields, transValue, self._macFormat)
        return buf



class Package(TransactionDesc):

    def __init__(self, fielddef, config):
        TransactionDesc.__init__(self, fielddef, config)
        self._bodyLenField = None
        self._packageLenField = None

    def pack(self, transDesc, transValue):
        body = transDesc.pack(transValue)
        # then deal all the fields presented
        header = ""
        indexes = self._fields.keys()
        indexes.sort()
        hasMac = 0
        packageLenPos = -1
        for index in indexes:
            field = self._fields[index]
            if field == self._bodyLenField:
                (value, dummy) = field.isofield.encode("%d" % len(body))
            elif field == self._packageLenField:
                packageLenPos = len(header)
                (value, dummy) = field.isofield.encode("0")
            else:
                (value, dummy) = field.isofield.encode(transValue[index]['host'])
            header += (value)
        if self._packageLenField != None:
            (value, dummy) = self._packageLenField.isofield.encode("%d" % (len(header)+len(body)))
            header = header[:packageLenPos] + value + header[packageLenPos+len(value):]
        print hexlify(header)+hexlify(body)+"\n"
        return (header + body)

    def unpackHeader(self, fielddef, data, transObj):
        msgDump = ''
        indexes = self._fields.keys()
        indexes.sort()
        for index in indexes:
            isofield = fielddef.fields_index_hash[index]
            (value, total_len) = isofield.decode(data)
            if isofield.fieldEnc.visible():
                msgDump += "Field[%s]:'%s'\n" % (isofield.name, value)
            else:
                msgDump += "Field[%s]:'%s'\n" % (isofield.name, hexlify(value))
            data = data[total_len:]
            transObj[index] = {'net' : data[0:total_len], 'host' : value}

        return (data, msgDump)

    def unpack(self, fielddef, data):
        transObj = {}
        msgDump = ''
        (data, headerDump) = self.unpackHeader(fielddef, data, transObj)
        (transObj, bodyDump) = fielddef.messageFormat.unpack(fielddef, data, transObj)
        print "header="+headerDump+"\n"
        print "body=" + bodyDump + "\n"
#        return (transObj, headerDump.encode('ascii')+bodyDump.encode('ascii'))
        return (transObj, bodyDump)


if (__name__ == "__main__"):
    import IsoFieldDef
    from DumpBinary import dumpBinary
    from Dictionary import LoadDictionaries
    import Configure

    Configure.LoadConfiguration("project/bos2.1.prj")

    dicts = LoadDictionaries("project/bos2.1/dictionary")
    fielddef = IsoFieldDef.LoadIsoFieldDef("project/bos2.1/Bos21FieldDef.xml", dicts)

    config = {}
    config['pinblock_mode'] = "08"
    config['zpk'] = "1C25E98F9B9249AB"
    config['zak'] = "04C7BA865EECA85E"

    transDesc = CreateTransDescObject(fielddef, "project/bos2.1/trans_cases/ExchangePinKeyTripleDes.xml", config)
#    transDesc = CreateTransDescObject(fielddef, "project/bos2.1/trans_cases/Sale.xml", config)

    transObj = {}
    transObj[0] = {'host' : "0200"}
    transObj[2] = {'host' : "4026740000001234"}
    transObj[3] = {'host' : "011000"}
    transObj[4] = {'host' : "10000"}
    transObj[7] = {'host' : "0609042030"}
    transObj[11] = {'host' : "123456"}
    transObj[12] = {'host' : "203000"}
    transObj[13] = {'host' : "0904"}
    transObj[15] = {'host' : "0904"}
    transObj[18] = {'host' : "6011"}
    transObj[22] = {'host' : "020"}
    transObj[23] = {'host' : "01"}
    transObj[25] = {'host' : "00"}
    transObj[26] = {'host' : "06"}
    transObj[32] = {'host' : "03112900"}
    transObj[33] = {'host' : "03112900"}
    transObj[35] = {'host' : "4026740000001234=081010100000123000"}
    transObj[37] = {'host' : "123456"}
    transObj[41] = {'host' : "001"}
    transObj[42] = {'host' : "100001"}
    transObj[43] = {'host' : "BANK OF SHANGHAI"}
    transObj[48] = {'host' : "NK"+unhexlify("1234567890ABCDEF")}
    transObj[49] = {'host' : "156"}
    transObj[52] = {'host' : "123456"}
    transObj[53] = {'host' : "1000000000000000"}
    transObj[55] = {'host' : "12345"}
    transObj[70] = {'host' : "101"}
    transObj[90] = {'host' : "020007631309071927010000102100000001021000"}
    transObj[96] = {'host' : unhexlify("1234567890ABCDEF")}
    transObj[100] = {'host' : "03112900"}
    transObj[121] = {'host' : "51100001403112900   "}
    transObj[123] = {'host' : "12345678"}
    buf = transDesc.pack(transObj)
    print buf
    print "\n\n"
    print dumpBinary(buf)

    print "\n\n"

    transObj = {}
    (transObj, buf) = transDesc._fielddef.messageFormat.unpack(transDesc._fielddef, buf, transObj)
    print transObj
    print buf

