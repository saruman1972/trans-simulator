from lxml import etree
import string
import re
from binascii import *
from ListFile import listFiles
from Utility import *

def LoadDictionary(filename):
#    try:
        doc = etree.parse(filename)
        root = doc.getroot()
        choices = []
        for elem in root.xpath("element"):
            if elem.attrib.has_key('desc'):
                desc = decodeXMLString(elem.attrib['desc'])
            else:
                desc = ''
            choices.append((desc, elem.attrib['value']))
        return (root.attrib['name'], choices)
#    except:
#        return ('',[])

def LoadDictionaries(path):
	dictionaries = {}
	dicts = listFiles(path, '*.xml', recurse=0)
	for dict in dicts:
		(name,choices) = LoadDictionary(dict)
		dictionaries[name] = choices
	return dictionaries


if (__name__ == "__main__"):
#	print LoadDictionary("project/bos1.0/dictionary/MccCode.xml")
	print LoadDictionaries("project/bos1.0/dictionary")
