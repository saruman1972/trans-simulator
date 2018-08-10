#!/usr/bin/python
# -*- coding: utf8 -*-

from binascii import *

def decodeXMLString(xmlString):
    return unicode(xmlString.encode("ISO-8859-1"), "gbk")
