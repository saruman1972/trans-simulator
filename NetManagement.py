
""" handle net management trxns (sign on, key exchange ...) """

import threading
import Queue
from NetManagementLog import NetManagementWin
from DumpBinary import dumpBinary
import string

class NetManagement(threading.Thread):

    def __init__(self, config, fielddef, package, managementDescs, switch, timeout=0.5):
        threading.Thread.__init__(self)
        self.package = package
        self.config = config
        self.fielddef = fielddef
        self.managementDescs = managementDescs
        self.queue = Queue.Queue()
        self.switch = switch
        self.timeout = 0.5
        self.active = True
        self.statusWin = None
        self.makeMessageTransMap()
    
    def addMessage(self, message):
        self.queue.put(message, timeout=self.timeout)
        
    def quit(self):
        # first destroy the status window
        if (self.statusWin != None):
            self.statusWin.Destroy()
            self.statusWin = None
        self.active = False
        
    def openService(self):
        self.start()
        self.statusWin = NetManagementWin(None, "Net Management")
        self.statusWin.Show(True)

    def run(self):
        from Switch import Switch
        """ process each incoming message """
        while (self.active):
            try:
                message = self.queue.get(timeout=self.timeout)
                print "Net Management got message**********"
                log = dumpBinary(message)
                print log
                self.statusWin.addIncomingMessage(log)
                (rcvObj, log) = self.package.unpack(self.fielddef, message)
                print log
                self.statusWin.addIncomingMessage(log)
            except:        # will get empty exception when timeout
                continue

            transDesc = self.findTransDesc(rcvObj)
            if transDesc == None:
                print "received message with no trans map"
                continue
            transObj = self.formTransObj(transDesc, rcvObj)
            message = self.package.pack(transDesc, transObj)
            self.switch.addMessage(message, Switch.MANAGEMENT_TRXN)
            
            # response message
            log = dumpBinary(message)
            print "Net Management repoinse message************"
            print log
            self.statusWin.addOutgoingMessage(log)
            (dummy, log) = self.package.unpack(self.fielddef, message)
            print log
            self.statusWin.addOutgoingMessage(log)
        
        print "end of management thread", self
        
    def formTransObj(self, transDesc, rcvObj):
        transObj = {}
        indexes = transDesc._fields.keys()
        indexes.sort()
        for index in indexes:
            field = transDesc._fields[index]
            if len(field.copy_field_maps) == 0:
                value = field.getValue(transObj)
            else:        # copy from msg received
                value = rcvObj[index]
            transObj[index] = {'host' : value}
            
        return transObj

    def makeMessageTransMap(self):
        self.messageTransMap = {}
        for transDesc in self.managementDescs:
            key = ''
            for field in transDesc.keyfields:
                key += "F%d" % field
            if self.messageTransMap.has_key(key) == False:
                self.messageTransMap[key] = {}
                self.messageTransMap[key]['fields'] = transDesc.keyfields
                self.messageTransMap[key]['map'] = {}
            self.messageTransMap[key]['map'][transDesc.keyvalue] = transDesc
            print "key=",key,self.messageTransMap[key]['fields'],"keyvalue=",transDesc.keyvalue

    def findTransDesc(self, rcvObj):
        print rcvObj
        for key in self.messageTransMap:
            keyvalue = ''
            print self.messageTransMap[key]['fields']
            for field in self.messageTransMap[key]['fields']:
                try:
                    keyvalue += rcvObj[field]
                except: pass
            print "keyvalue=", keyvalue
            if self.messageTransMap[key]['map'].has_key(keyvalue):
                return self.messageTransMap[key]['map'][keyvalue]
        return None
        

if __name__ == "__main__":
    print Switch.MANAGEMENT_TRXN
    
