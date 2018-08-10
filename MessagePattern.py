
class Block:

    def __init__(self):
        self.transObj = []
        
    def pack(self, info): pass

    def unpack(self): pass
    
class Body(Block):

    def __init__(self):
        Block.__init__(self)
        self.conent = None

    def setBodyContent(self, content):
        self.content = content
        
    def pack(self, info):
        return self.content.pack(info)

    def unpack(self, message):
        return self.content.unpack(message)
                
class Header(Block):

    def __init__(self):
        self.fields = []
        Block.__init__(self)

    def blockLength(self):
        length = 0
        for field in self.fields:
            length += field.isofield.length()
        return length
    
    def addField(self, field):
        self.fields.append(field)

    def pack(self, info):
        message = ""
        for field in self.fields:
            value = field.getValue(info)
            (value, dummy) = field.isofield.encode(value)
            message += value
        return message
        
    def unpack(self, message):
        obj = []
        tot_len = 0
        for field in self.fields:
            (value, length) = field.isofield.decode(message)
            message = message[length:]
            obj.append(value)
            tot_len += length
        return (obj, tot_len)

class PackageHeader(Header):

    def __init__(self):
        Header.__init__(self)
        
    def unpack(self, message):
        packageLen = 0
        head_len = 0
        for field in self.fields:
            (value, length) = field.isofield.decode(message)
            message = message[length:]
            if field.isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginPackageLength:
                packageLen = string.atoi(value)
            head_len += length
        return (packageLen, head_len)

class PackagePattern(Block):

    def __init__(self):
        Block.__init__(self)
        self.header = None
        self.body = None
        
    def blockLength(self):
        return self.header.blockLength()
        
    def setHeader(self, header):
        self.header = header
        
    def setBody(self, body):
        self.body = body
        
    def pack(self, info):
        body = self.body.pack(info)
        header = self.header.pack((self.header, body))
        return (header, body)

class MessagePattern(PackagePattern):

    def __init__(self):
        PackagePattern.__init__(self)
        
    def pack(self, info):
        (header,body) = PackagePattern.pack(self, info)
        return header + body

    def unpack(self, message):
        (head_objs, head_len) = self.header.unpack(message)
        message = message[tot_len:]
        (objs, body, body_len) = self.body.unpack(message)
        if objs == None:
            head = head_objs
        else:
            head = [head_objs, objs]
        return (head, body, head_len+body_len)
    
class MessageContent(Block):

    def __init__(self):
        Block.__init__(self)
    
    def pack(self, info):
        return info

    def unpack(self, message):
        return (None, message, len(message))
