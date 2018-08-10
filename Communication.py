#!/usr/bin/python
# -*- coding: utf8 -*-

from socket import *
from select import *
import string
import threading
import Queue
import time
import wx
from IsoFieldDef import *
import Switch
from NetStatus import NetStatusWin
from DumpBinary import dumpBinary

class AsciiLengthField:
    def __init__(self, size):
        self.size = size

    def encode(self, length):
        var = "%0*.*d" % (self.size, self.size, length)
        return (var, self.size)

    def decode(self, buffer):
        var = buffer[:self.size]
        return (string.atoi(var), self.size)

class BinaryLengthField:
    def __init__(self, size):
        self.size = size

    def encode(self, length):
        var = ""
        while (length > 0):
            byte = length & 0xff
            length >>= 8
            var = chr(byte) + var
        fill_char = chr(0x00)
        length = len(var)
        var = fill_char*(self.size-length) + var    # 左补0
        return (var, self.size)

    def decode(self, buffer):
        len_str = buffer[:self.size]
        val = 0
        for ch in len_str:
            val <<= 8
            val += ord(ch)
        return (val, self.size)

class Communication:
    """ communication abstract base class, should be inherited """

    def __init__(self, config, switch=None):
        self.config = config
        self.active = True
        self.switch = switch
        self.sendThread = None
        self.receiveThread = None

        self.sndBreakEvent = threading.Event()
        self.sndBreakEvent.set()
        self.rcvBreakEvent = threading.Event()
        self.rcvBreakEvent.set()

        self.initMessagePattern(self.config)

    def quit(self):
        print "Communication quiting"
        self.active = False
        if (self.sendThread != None):
            self.sendThread.quit()
        if (self.receiveThread != None):
            self.receiveThread.quit()

    def setSwitch(self, switch):
        self.switch = switch

    def initMessagePattern(self, config):
        self.messagePattern = []
        self.messageHeadLen = 0
        for (key,val) in config['message_head_pattern']:
            if (key == 'length'):
                length = val['len']
                encode = val['encode']
                encode.upper()

                if (encode == "ASCII"):
                    field_length = AsciiLengthField(length)
                else:
                    field_length = BinaryLengthField(length)

                self.messagePattern.append(('length', field_length, length))
                self.messageHeadLen += length
            else:    # key should be 'fill'
                fill_char = val['char']
                length = val['len']

                field_fill = DataField()
                field_fill.fieldEnc = fieldEncodeMap['FE_A']
                field_fill.fieldType = fieldTypeMap['FT_FIXED']
                field_fill.size = length

                self.messagePattern.append(('fill', field_fill, fill_char))
                self.messageHeadLen += length

    def packMessageHead(self, message):
        messageHeader = ""
        for (key, field, val) in self.messagePattern:
            if (key == 'length'):
                length = len(message)
                (var, dummy) = field.encode(length)
                messageHeader += var
            elif (key == 'fill'):
                fill = val * field.size
                (var,dummy) = field.encode(fill)
                messageHeader += var
            else:
                raise ValueError('invalid key [' + key + ']')
        return messageHeader

    def unpackMessageHead(self, messageHeader):
        for (key, field, val) in self.messagePattern:
            if (key == 'length'):
                (var, var_len) = field.decode(messageHeader)
                return var
            elif (key == 'fill'):
                messageHeader = messageHeader[field.size:]
            else:
                raise ValueError('invalid key [' + key + ']')
        return 0

    def setSendSocket(self, sndSocket):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def setReceiveSocket(self, rcvSocket):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def setSendBreakEvent(self):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def setReceiveBreakEvent(self):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def openCommunication(self):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def closeCommunication(self):
        # set active False will force all the threads terminate themselvs
        self.active = False

    def logIncomingMessage(self, message):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def logOutgoingMessage(self, message):
        """ template function, should be inheritated """
        raise ValueError('abstract base class should never be instanciated')

    def sendMessage(self, message):
        # delegate to the sending thread
        if (self.sendThread != None):
            self.sendThread.addMessage(message)
        else:
            print "sending thread not ready"


class SimplexCommunication(Communication):
    """ simplex communication main class """

    def __init__(self, config, switch=None):
        Communication.__init__(self, config, switch)
        self.clientThread = None
        self.serverThread = None

        self.clientStatusWin = None
        self.serverStatusWin = None

    def quit(self):
        # first destroy the status window
        if (self.clientStatusWin != None):
            self.clientStatusWin.Destroy()
            self.clientStatusWin = None
        if (self.serverStatusWin != None):
            self.serverStatusWin.Destroy()
            self.serverStatusWin = None

        Communication.quit(self)
        if (self.clientThread != None):
            self.clientThread.quit()
        if (self.serverThread != None):
            self.serverThread.quit()

    def setSendBreakEvent(self):
        self.sendThread = None
        self.sndBreakEvent.set()

    def setReceiveBreakEvent(self):
        self.receiveThread = None
        self.rcvBreakEvent.set()

    def openCommunication(self):
        self.active = True

        # create status window
        try:
            self.clientStatusWin = NetStatusWin(None, "Client Status")
            self.clientStatusWin.Show(True)
            self.serverStatusWin = NetStatusWin(None, "Server Status")
            self.serverStatusWin.Show(True)
        except:
            self.clientStatusWin = None
            self.serverStatusWin = None

        # simplex communication should open both client and server socket
        dstIP = self.config['remote']['ip']
        dstPort = self.config['remote']['port']
        self.clientThread = ClientThread(self, dstIP, dstPort)
        self.clientThread.start()

        localPort = self.config['local']['port']
        self.serverThread = ServerThread(self, localPort)
        self.serverThread.start()

    def setSendSocket(self, sndSocket):
        # connect ok, start the send daemon
        self.sndBreakEvent.clear()
        self.sendThread = SendThread(self, sndSocket)
        self.sendThread.start()

    def setReceiveSocket(self, rcvSocket):
        # connect ok, start the receive daemon
        self.rcvBreakEvent.clear()
        self.receiveThread = ReceiveThread(self, rcvSocket)
        self.receiveThread.start()

    def logIncomingMessage(self, message):
        msg = dumpBinary(message)
        if (self.serverStatusWin != None):
            wx.CallAfter(self.serverStatusWin.addMsg, msg)

    def logOutgoingMessage(self, message):
        msg = dumpBinary(message)
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.addMsg, msg)


class ShortTermClientCommunication(Communication):
    """ short term client communication client main class """

    def __init__(self, config, switch=None):
        Communication.__init__(self, config, switch)
        self.clientStatusWin = None
        self.receive_timeout = 10.0
        self.select_timeout = 1.0

    def quit(self):
        # first destroy the status window
        if (self.clientStatusWin != None):
            self.clientStatusWin.Destroy()
            self.clientStatusWin = None

        Communication.quit(self)

    def sendMessage(self, message):
        # show status
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.SetTitle, "Client site")
            wx.CallAfter(self.clientStatusWin.setTip, "connecting to %s:%d" % (self.dstIP, self.dstPort))

        # socket broken, make a new connection
        sndSocket = socket(AF_INET, SOCK_STREAM)
        connectOk = False
        while (self.active and (connectOk == False)):
            try:
                sndSocket.connect((self.dstIP, self.dstPort))
                connectOk = True

                # show status
                if (self.clientStatusWin != None):
                    wx.CallAfter(self.clientStatusWin.setTip, "%s:%d connected" % (self.dstIP, self.dstPort))
            except:        # wait for 1 sec to reconnect
                time.sleep(1)
        self.send(message, sndSocket)
        self.receive(sndSocket)
                    
    def send(self, message, sndSocket):
        header = self.packMessageHead(message)
        sndSocket.send(header)
        self.logOutgoingMessage(header + message)
        print "send message:==================\n"
        print dumpBinary(header)
        print dumpBinary(message)
        print "===============================\n"
        nbytes = len(message)
        while (self.active and (nbytes > 0)):
            byte_snds = sndSocket.send(message)
            if (byte_snds == 0):        # socket has broken
                raise ValueError('socket has broken')
            print "=============>", message[:byte_snds]
            message = message[byte_snds:]
            nbytes -= byte_snds
        
    def receive(self, rcvSocket):
        messageHead = rcvSocket.recv(self.messageHeadLen)
        if (messageHead == ""):    # socket has broken
            raise ValueError('socket has broken')
        msgLen = self.unpackMessageHead(messageHead)

        curLen = 0
        msg = ""
        startT = time.time()
        while (self.active and (curLen < msgLen)):
            t = time.time()
            if (t - startT > self.receive_timeout):
                # timeout, discard this message
                self.logIncomingMessage("!!!!!!!! receive time out !!!!!!!!!")
                return

            (rlist,wlist,elist) = select([rcvSocket], [], [], self.select_timeout)
            if (len(rlist) == 0):    # not ready yet, continue looping
                continue
            curMsg = rcvSocket.recv(msgLen-curLen)
            if (curMsg == None):    # socket has broken
                raise ValueExceptino('socket has broken')
            msg += curMsg
            curLen += len(curMsg)

        self.logIncomingMessage(messageHead + msg)

        # send to the switch queue if exist
        if (self.switch != None):
            self.switch.addMessage(msg, None)
        
    def openCommunication(self):
        self.active = True
        
        # create status window
        try:
            self.clientStatusWin = NetStatusWin(None, "Client Status")
            self.clientStatusWin.Show(True)
        except:
            self.clientStatusWin = None

        self.dstIP = self.config['remote']['ip']
        self.dstPort = self.config['remote']['port']

    def logIncomingMessage(self, message):
        msg = dumpBinary(message)
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.addMsg, msg)

    def logOutgoingMessage(self, message):
        msg = dumpBinary(message)
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.addMsg, msg)

class DuplexClientCommunication(Communication):
    """ full duplex communication client main class """

    def __init__(self, config, switch=None):
        Communication.__init__(self, config, switch)
        self.clientThread = None
        self.clientStatusWin = None

    def quit(self):
        # first destroy the status window
        if (self.clientStatusWin != None):
            self.clientStatusWin.Destroy()
            self.clientStatusWin = None

        Communication.quit(self)
        if (self.clientThread != None):
            self.clientThread.quit()

    def setSendBreakEvent(self):
        self.sendThread = None
        self.receiveThread = None
        # should set both event
        self.sndBreakEvent.set()
        self.rcvBreakEvent.set()

    def setReceiveBreakEvent(self):
        self.sendThread = None
        self.receiveThread = None
        # should set both event
        self.rcvBreakEvent.set()
        self.sndBreakEvent.set()

    def openCommunication(self):
        self.active = True

        # create status window
        try:
            self.clientStatusWin = NetStatusWin(None, "Client Status")
            self.clientStatusWin.Show(True)
        except:
            self.clientStatusWin = None

        # duplex communication client should only open client socket
        dstIP = self.config['remote']['ip']
        dstPort = self.config['remote']['port']
        self.clientThread = ClientThread(self, dstIP, dstPort)
        self.clientThread.start()

    def setSendSocket(self, sndSocket):
        # connect ok, start the send and receive daemon
        self.sndBreakEvent.clear()
        self.rcvBreakEvent.clear()

        self.sendThread = SendThread(self, sndSocket)
        self.sendThread.start()

        self.receiveThread = ReceiveThread(self, sndSocket)
        self.receiveThread.start()

    def logIncomingMessage(self, message):
        msg = dumpBinary(message)
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.addMsg, msg)

    def logOutgoingMessage(self, message):
        msg = dumpBinary(message)
        if (self.clientStatusWin != None):
            wx.CallAfter(self.clientStatusWin.addMsg, msg)


class DuplexServerCommunication(Communication):
    """ full duplex communication server main class """

    def __init__(self, config, switch=None):
        Communication.__init__(self, config, switch)
        self.serverThread = None
        self.serverStatusWin = None

    def quit(self):
        # first destroy the status window
        if (self.serverStatusWin != None):
            self.serverStatusWin.Destroy()
            self.serverStatusWin = None

        Communication.quit(self)
        if (self.serverThread != None):
            self.serverThread.quit()

    def setSendBreakEvent(self):
        self.sendThread = None
        self.receiveThread = None
        # should set both event
        self.sndBreakEvent.set()
        self.rcvBreakEvent.set()

    def setReceiveBreakEvent(self):
        self.sendThread = None
        self.receiveThread = None
        # should set both event
        self.rcvBreakEvent.set()
        self.sndBreakEvent.set()

    def openCommunication(self):
        self.active = True

        # create status window
        try:
            self.serverStatusWin = NetStatusWin(None, "Server Status")
            self.serverStatusWin.Show(True)
        except:
            self.serverStatusWin = None

        # duplex communication client should only open server socket
        localPort = self.config['local']['port']
        self.serverThread = ServerThread(self, localPort)
        self.serverThread.start()

    def setReceiveSocket(self, rcvSocket):
        # connect ok, start the send and receive daemon
        self.sndBreakEvent.clear()
        self.rcvBreakEvent.clear()

        self.sendThread = SendThread(self, rcvSocket)
        self.sendThread.start()

        self.receiveThread = ReceiveThread(self, rcvSocket)
        self.receiveThread.start()

    def logIncomingMessage(self, message):
        msg = dumpBinary(message)
        if (self.serverStatusWin != None):
            wx.CallAfter(self.serverStatusWin.addMsg, msg)

    def logOutgoingMessage(self, message):
        msg = dumpBinary(message)
        if (self.serverStatusWin != None):
            wx.CallAfter(self.serverStatusWin.addMsg, msg)




class ClientThread(threading.Thread):
    """ socket client class, monitor the creation of connection """

    def __init__(self, comm, dstIP, dstPort, timeout=1.0):
        threading.Thread.__init__(self)
        self.comm = comm;
        self.dstIP = dstIP
        self.dstPort = dstPort
        self.timeout = timeout
        self.active = True

    def quit(self):
        self.active = False
        print "Client Thread quiting"

    def run(self):
        """ main loop, monitor the socket status """
        """ use template function pattern """
        while self.active:
            # wait for the socket broken event
            # note: sndBreakEvent and rcvBreakEvent will both be set both in the
            #       snd/rcv thread if the communication mode is full duplex
            #       so wait for any event will work
            self.comm.sndBreakEvent.wait(self.timeout)
            if (self.comm.sndBreakEvent.isSet() == False):
                # socket still alive, do nothing around
                continue

            # wait for daemon thread termination
            time.sleep(3)

            # show status
            if (self.comm.clientStatusWin != None):
                wx.CallAfter(self.comm.clientStatusWin.SetTitle, "Client site")
                wx.CallAfter(self.comm.clientStatusWin.setTip, "connecting to %s:%d" % (self.dstIP, self.dstPort))

            # socket broken, make a new connection
            sndSocket = socket(AF_INET, SOCK_STREAM)
            connectOk = False
            while (self.active and (connectOk == False)):
                try:
                    sndSocket.connect((self.dstIP, self.dstPort))
                    connectOk = True
                    self.comm.setSendSocket(sndSocket)

                    # show status
                    if (self.comm.clientStatusWin != None):
                        wx.CallAfter(self.comm.clientStatusWin.setTip, "%s:%d connected" % (self.dstIP, self.dstPort))
                except:        # wait for 5 sec to reconnect
                    time.sleep(5)

        print "Client Thread Terminated"


class ServerThread(threading.Thread):
    """ socket client class, monitor the creation of connection """

    def __init__(self, comm, port, timeout=1.0):
        threading.Thread.__init__(self)
        self.comm = comm
        self.port = port
        self.timeout = timeout
        self.active = True

    def quit(self):
        self.active = False
        print "Server Thread quiting"

    def run(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
#       self.socket.bind((gethostbyname(gethostname()), self.port))
        self.socket.bind(("", self.port))
        self.socket.listen(1)        # only 1 connection permited simultaneously

        while self.active:
            # wait for the socket broken event
            # note: sndBreakEvent and rcvBreakEvent will both be set in the
            #       snd/rcv thread if the communication mode is full duplex
            #       so wait for any event will work
            self.comm.rcvBreakEvent.wait(self.timeout)
            if (self.comm.rcvBreakEvent.isSet() == False):
                # socket still alive, do nothing around
                continue

            # show status
            if (self.comm.serverStatusWin != None):
                wx.CallAfter(self.comm.serverStatusWin.SetTitle, "Server Site")
                wx.CallAfter(self.comm.serverStatusWin.setTip, "waiting for connection...")

            connectOk = False
            while (self.active and (connectOk == False)):
                (rlist,wlist,elist) = select([self.socket], [], [], self.timeout)
                if (len(rlist) == 0):    # no incoming connection, continue looping
                    continue

                (rcvSocket, addressInfo) = self.socket.accept()
                connectOk = True
                self.comm.setReceiveSocket(rcvSocket)

                # show status
                if (self.comm.serverStatusWin != None):
                    wx.CallAfter(self.comm.serverStatusWin.setTip, "connected with " + addressInfo[0])
                print "connected with " + addressInfo[0]

        self.socket.close()
        print "Server Thread Terminated"








class SendThread(threading.Thread):
    """ daemon thread to send message to network """

    def __init__(self, comm, sndSocket, timeout=1.0):
        threading.Thread.__init__(self)
        self.comm = comm
        self.sndSocket = sndSocket
        self.timeout = timeout
        self.queue = Queue.Queue()        # input queue
        self.active = True

    def quit(self):
        self.active = False
        print "Send Thread quiting"

    def addMessage(self, message):
        self.queue.put(message)

    def run(self):
        while (self.active and (self.comm.sndBreakEvent.isSet() == False)):
            try:
                message = self.queue.get(timeout=self.timeout)
            except:        # will get empty exception when timeout
                continue

            try:
                self.send(message)
            except:        # socket broken
                self.sndSocket.close()
                self.sndSocket = None
                # set send socket break event to let parent reestablish the communication
                self.comm.setSendBreakEvent()

        # fall through here to terminate the current thread
        # new thread will be created after the communication reestablished
        print self,"Send Thread Terminated"
        self.sndSocket.close()

    def send(self, message):
        header = self.comm.packMessageHead(message)
        self.sndSocket.send(header)
        self.comm.logOutgoingMessage(header + message)
        print "send message:==================\n"
        print dumpBinary(header)
        print dumpBinary(message)
        print "===============================\n"
        nbytes = len(message)
        while (self.active and (nbytes > 0)):
            byte_snds = self.sndSocket.send(message)
            if (byte_snds == 0):        # socket has broken
                raise ValueError('socket has broken')
            print "=============>", message[:byte_snds]
            message = message[byte_snds:]
            nbytes -= byte_snds



class ReceiveThread(threading.Thread):
    """ daemon thread to receive message from network """

    def __init__(self, comm, rcvSocket, receive_timeout=10, select_timeout=1.0):
        threading.Thread.__init__(self)
        self.comm = comm
        self.rcvSocket = rcvSocket
        self.receive_timeout = receive_timeout
        self.select_timeout = select_timeout
        self.active = True

    def quit(self):
        self.active = False
        print "Receive Thread quiting"

    def run(self):
        try:
            self.receive()
        except:        # socket broken
            self.rcvSocket.close()
            self.rcvSocket = None
            # set receive socket break event to let parent reestablish the communication
            self.comm.setReceiveBreakEvent()

        # fall through here to terminate the current thread
        # new thread will be created after the communication reestablished
        print self,"Receive Thread Terminated"
        if self.rcvSocket:
            self.rcvSocket.close()

    def receive(self):
        while self.active:
            (rlist,wlist,elist) = select([self.rcvSocket], [], [], self.select_timeout)
            if (len(rlist) == 0):    # not ready yet, continue looping
                continue

            messageHead = self.rcvSocket.recv(self.comm.messageHeadLen)
            if (messageHead == ""):    # socket has broken
                raise ValueError('socket has broken')
            msgLen = self.comm.unpackMessageHead(messageHead)

            curLen = 0
            msg = ""
            startT = time.time()
            while (self.active and (curLen < msgLen)):
                t = time.time()
                if (t - startT > self.receive_timeout):
                    # timeout, discard this message
                    return

                (rlist,wlist,elist) = select([self.rcvSocket], [], [], self.select_timeout)
                if (len(rlist) == 0):    # not ready yet, continue looping
                    continue
                curMsg = self.rcvSocket.recv(msgLen-curLen)
                if (curMsg == None):    # socket has broken
                    raise ValueExceptino('socket has broken')
                msg += curMsg
                curLen += len(curMsg)

            self.comm.logIncomingMessage(messageHead + msg)

            # send to the switch queue if exist
            if (self.comm.switch != None):
                self.comm.switch.addMessage(msg, None)










if (__name__ == "__main__"):
    from Configure import *
    config = LoadConfiguration("project/jcb.prj")
#    comm = SimplexCommunication(config)
#    comm = DuplexClientCommunication(config)
    comm = DuplexServerCommunication(config)

    message = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    header = comm.packMessageHead(message)
    print header + "|||||"
    print hexlify(header)

    print "\n\n"
    length = comm.unpackMessageHead(header)
    print length

#    comm.openCommunication()

