#!/usr/bin/python
# -*- coding: utf8 -*-

import threading
import Queue
import time
import Communication
from NetManagement import NetManagement

class MessageKey:

    MESSAGE_REQUEST = 0
    MESSAGE_RESPONSE = 1

    def __init__(self, transObj, fields):
        message_type = transObj[0]['host']
        if (ord(message_type[2]) & 0x01):
            self.type = MessageKey.MESSAGE_RESPONSE
        else:
            self.type = MessageKey.MESSAGE_REQUEST
        actual_message_type = message_type[:2]
        actual_message_type += chr(ord(message_type[2]) & 0xFE)
        actual_message_type += message_type[3:]
        self.key_str = actual_message_type

        for field in fields:
            self.key_str += transObj[field]['host']

    def key(self):
        return self.key_str

class Switch(threading.Thread):

    NORMAL_TRXN = 0                    # simulator ==> issure
    MANAGEMENT_TRXN = 1                # issure ==> simulator

    def __init__(self, config, fielddef, package, queueTimeOut=0.5, transTimeOut=30):
        threading.Thread.__init__(self)
        self.config = config
        self.fielddef = fielddef
        self.package = package
        self.keyFields = config['store_table_fields']
        self.queueTimeOut = queueTimeOut
        self.transTimeOut = transTimeOut
        self.active = True
        self.messages = {}
        self.queue = Queue.Queue()

        self.management_thread = None        # management thread
        self.transaction_thread = None        # transaction thread
        self.communication_thread = None    # communication thread

    def setTransactionThread(self, transaction_thread):
        self.transaction_thread = transaction_thread

    def addMessage(self, message, type):
        self.queue.put((message, type), timeout=self.queueTimeOut)

    def quit(self):
        self.active = False
        self.communication_thread.quit()
        self.management_thread.quit()

    def online(self):
        # begin working, power on each slave thread
        communication_type = self.config['communication_type']
        if (communication_type == 'simplex'):
            self.communication_thread = Communication.SimplexCommunication(self.config, self)
        elif (communication_type == 'duplex_client'):
            self.communication_thread = Communication.DuplexClientCommunication(self.config, self)
        elif (communication_type == 'duplex_server'):
            self.communication_thread = Communication.DuplexServerCommunication(self.config, self)
        elif (communication_type == 'shortterm_client'):
            self.communication_thread = Communication.ShortTermClientCommunication(self.config, self)
        else:
            raise ValueError('invalid communication type[' + communication_type + ']')
        self.communication_thread.openCommunication()

        management_cases = self.config['management_cases']
        self.management_thread = NetManagement(self.config, self.fielddef, self.package, management_cases, self)
        self.management_thread.openService()

        self.start()

    def run(self):
        """ main thread, do message dispatching """
        while (self.active):
            try:
                (message, type) = self.queue.get(timeout=self.queueTimeOut)
            except:        # will get empty exception when timeout
                continue
            print "Switch got message:===================\n"
            (transObj, log) = self.transaction_thread._package.unpack(self.fielddef, message)
            print log
            print "======================================\n\n"

            try:
                key = MessageKey(transObj, self.keyFields)
            except:
                print "make key for store table error"
                continue

            if (key.type == MessageKey.MESSAGE_REQUEST):
                """ 保存两种消息，一种是从simulator发起的，一种是从issuer发起的（如签到、网络管理等） """
                if (self.messages.has_key(key.key())):
                    raise ValueError('key[' + key.key() + '] already exists')
                # store the message type and time
                inTime = time.time()
                self.messages[key.key()] = (type, inTime)

                if (type == Switch.NORMAL_TRXN):
                    # sending the message to issure
                    if (self.communication_thread != None):
                        self.communication_thread.sendMessage(message)
                    else:
                        print "communication thread not ready"
                else:
                    print "management message received"
                    # send the message to management thread
                    if (self.management_thread != None):
                        self.management_thread.addMessage(message)
                    else:
                        print "management thread not ready"

            else:    # message response
                if self.messages.has_key(key.key()):
                    curTime = time.time()
                    (type, inTime) = self.messages[key.key()]
                    print "response time=", curTime-inTime
                    # remove from matching table
                    del self.messages[key.key()]
                    if (curTime-inTime > self.transTimeOut):
                        # message has timeout, discard it
                        continue
                    if (type == Switch.NORMAL_TRXN):
                        # send back the message to original transaction
                        if (self.transaction_thread != None):
                            self.transaction_thread.addMessage(message)
                        else:
                            print "transaction thread not ready"
                    else:        # should be MANAGEMENT_TRXN
                        # send back to issure
                        if (self.communication_thread != None):
                            self.communication_thread.sendMessage(message)
                        else:
                            print "communication thread not ready"
                else:
                    # havn't found matched request message, discard it
                    print "havn't found matched message", key.key()
                    pass
        print self, "Switch thread terminated"



if (__name__ == "__main__"):
    import IsoFieldDef
    fielddef = IsoFieldDef.LoadIsoFieldDef("IsoFieldDef.xml")
    from Configure import *
    config = LoadConfiguration("aaaa.xml")

    switch = Switch(fielddef, config)
    comm = SimplexCommunication(config, switch)
