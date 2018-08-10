from lxml import etree
import string
import re
from binascii import *
from Utility import *

config = {}

def LoadTag(node, tag, key=None):
    if key == None:
        key = tag
    elems = node.xpath(tag)
    if len(elems) == 0:
        config[key] = ""
    else:
        config[key] = decodeXMLString(elems[0].text.strip()).encode("utf8")

def LoadAttrib(node, tag, attr, key=None):
    if key == None:
        key = tag
    elems = node.xpath(tag)
    if len(elems) == 0:
        config[key] = ""
    elif elems[0].attrib.has_key(attr):
        config[key] = decodeXMLString(elems[0].attrib[attr]).encode("utf8")
    else:
        config[key] = ""

def LoadConfiguration(filename):
#    try:
    if True:
        doc = etree.parse(filename)
        root = doc.getroot()

        global config
        config = {}
        LoadTag(root, "name")
        LoadAttrib(root, "field_def", "file")
        LoadAttrib(root, "transaction_cases", "path", "transaction_cases_path")
        LoadAttrib(root, "management_cases", "path", "management_cases_path")
        LoadAttrib(root, "dictionary", "path", "dictionary_path")
        LoadTag(root, "pinblock_mode")
        LoadTag(root, "zmk")
        LoadTag(root, "zpk")
        LoadTag(root, "zak")
        LoadTag(root, "mk_ac")
        LoadTag(root, "mk_smi")
        LoadTag(root, "mk_smc")
        LoadTag(root, "trace_no")
        LoadTag(root, "batch_no")

        LoadTag(root, "org")
        LoadTag(root, "version")

        config['store_table_fields'] = []
        config['message_head_pattern'] = []

        for elem in root.xpath("store_table_fields/field"):
            config['store_table_fields'].append(string.atoi(elem.attrib['index']))

        for elem in root.xpath("communication/*"):
            if elem.tag == "type":
                config['communication_type'] = elem.text.strip()
            elif elem.tag == "remote":
                config['remote'] = {}
                if elem.attrib.has_key('ip'):
                    config['remote']['ip'] = elem.attrib['ip']
                else:
                    config['remote']['ip'] = '127.0.0.1'
                if elem.attrib.has_key('port'):
                    config['remote']['port'] = string.atoi(elem.attrib['port'])
                else:
                    config['remote']['port'] = '54321'
            elif elem.tag == "local":
                config['local'] = {}
                if elem.attrib.has_key('port'):
                    config['local']['port'] = string.atoi(elem.attrib['port'])
                else:
                    config['local']['port'] = '54321'
            elif elem.tag == "message_head_pattern":
                for e in elem.getchildren():
                    if e.tag == "length":
                        if e.attrib.has_key("encode"):
                            length_encode = e.attrib["encode"]
                        else:
                            length_encode = "ASCII"
                        config['message_head_pattern'].append(('length', {'len' : string.atoi(e.text.strip()), 'encode' : length_encode}))

                    if e.tag == "fill":
                        if e.attrib.has_key("char"):
                            fill_char = e.attrib['char']
                            if (re.match('0(x|X).*', fill_char)):
                                  fill_char = re.sub('0(x|X)', '', fill_char)
                                  fill_char = unhexlify(fill_char)
                        else:
                            fill_char = chr(0x00)
                        config['message_head_pattern'].append(('fill', {'len' : string.atoi(e.text.strip()), 'char' : fill_char}))

        return config
    else:
        return {}

def SaveConfiguration(filename, config):
    file = open(filename, 'w')
    file.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n")
    file.write("<configuration>\n")
    file.write("\t<name> " + config['name'] + " </name>\n")
    file.write("\t<field_def file=\"" + config['field_def'] + "\" />\n")
    file.write("\t<transaction_cases path=\"" + config['transaction_cases_path'] + "\" />\n")
    file.write("\t<management_cases path=\"" + config['management_cases_path'] + "\" />\n")
    file.write("\t<dictionary path=\"" + config['dictionary_path'] + "\" />\n")
    file.write("\t<communication>\n")
    file.write("\t\t<type> " + config['communication_type'] + " </type>\n")
    if config.has_key('remote'):
        file.write("\t\t<remote ip=\"" + config['remote']['ip'] + "\" port=\"" + str(config['remote']['port']) + "\" />\n")
    if config.has_key('local'):
        file.write("\t\t<local port=\"" + str(config['local']['port']) + "\" />\n\n")
    file.write("\t\t<message_head_pattern>\n")
    for (key,val) in config['message_head_pattern']:
        file.write("\t\t\t")
        if (key == 'length'):
            len = "%d" % val['len']
            file.write("<length encode=\"" + val['encode'] + "\"> " + len + " </length>\n")
        else:    # key should be 'fill'
            fill_char = "0x" + hexlify(val['char'])
            len = "%d" % val['len']
            file.write("<fill char=\"" + fill_char + "\"> " + len + " </fill>\n")
    file.write("\t\t</message_head_pattern>\n")
    file.write("\t</communication>\n")
    file.write("\t<pinblock_mode> " + config['pinblock_mode'] + " </pinblock_mode>\n");
    file.write("\t<zmk> " + config['zmk'] + " </zmk>\n");
    file.write("\t<zpk> " + config['zpk'] + " </zpk>\n");
    file.write("\t<zak> " + config['zak'] + " </zak>\n\n");
    file.write("\t<mk_ac> " + config['mk_ac'] + " </mk_ac>\n\n");
    file.write("\t<mk_smi> " + config['mk_smi'] + " </mk_smi>\n\n");
    file.write("\t<mk_smc> " + config['mk_smc'] + " </mk_smc>\n\n");
    file.write("\t<trace_no> " + config['trace_no'] + " </trace_no>\n");
    file.write("\t<batch_no> " + config['batch_no'] + " </batch_no>\n");
    file.write("\n");
    file.write("\t<store_table_fields>\n");
    for index in config['store_table_fields']:
        file.write("\t\t<field index=\"%d\" />\n" % index)
    file.write("\t</store_table_fields>\n");
    file.write("</configuration>\n")
    file.close()

if (__name__ == "__main__"):
    config = LoadConfiguration("project/visa.prj")
    print config

#    SaveConfiguration("aaaa.xml", config)
