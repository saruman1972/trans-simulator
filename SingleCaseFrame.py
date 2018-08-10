#!/usr/bin/python
# -*- coding: utf8 -*-

import threading
import  sys
import  cPickle
import  wx
import time
import Queue
from ScrolledFrame import ScrolledFrame
import  wx.lib.mixins.listctrl  as  listmix
from Switch import Switch
from DumpBinary import dumpBinary
import time
import datetime
import locale

class TransactionThread(threading.Thread):

    def __init__(self, frame, timeout=0.5):
        threading.Thread.__init__(self)
        self.frame = frame
        self.active = True
        self.timeout = timeout
        self.sndEvent = threading.Event()

    def quit(self):
        self.active = False

    def setSendEvent(self):
        self.sndEvent.set()

    def run(self):
        while self.active:
            self.sndEvent.wait(self.timeout)
            if (self.sndEvent.isSet() != True):
                continue

            self.sndEvent.clear()
            self.frame.doTransaction()



class TrxnListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Populate()
        listmix.TextEditMixin.__init__(self)

        self.trxns = []

        # facility for drag and drop
        wx.EVT_LEFT_DOWN(self, self.OnLeftDown)

    def Populate(self):
        self.InsertColumn(0, "case")
        self.InsertColumn(1, "field 2")
        self.InsertColumn(2, "field 3")
        self.InsertColumn(3, "field 4")
        self.InsertColumn(4, "field 7")
        self.InsertColumn(5, "field 11")
        self.InsertColumn(6, "field 22")
        self.InsertColumn(7, "field 25")
        self.InsertColumn(8, "field 32")
        self.InsertColumn(9, "field 33")
        self.InsertColumn(10, "field 49")
        self.InsertColumn(11, "field 38")
        self.InsertColumn(12, "field 39")

    def InsertTrxn(self, name, transObj, rcvObj):
        self.trxns.append((transObj, rcvObj))
        item = self.InsertStringItem(sys.maxint, name)
        self.SetStringItem(item, 0, name)
        seq = 1
        for index in [2,3,4,7,11,22,25,32,33,49]:
            try:
                value = transObj[index]['host']
                self.SetStringItem(item, seq, value)
            except:
                pass
            seq = seq + 1
        for index in [38,39]:
            try:
                value = rcvObj[index]
                self.SetStringItem(item, seq, value)
            except:
                pass
            seq = seq + 1

        self.SetItemData(item, len(self.trxns)-1)

    def OnLeftDown(self, event):
        x = event.GetX()
        y = event.GetY()
        item, flags = self.HitTest((x,y))

        if flags & wx.LIST_HITTEST_ONITEM:
#            self.Select(item)
            index = self.GetItemData(item)
            self.StartDragOperation(self.trxns[index])

        event.Skip()

    def StartDragOperation(self, objPair):
        data = wx.CustomDataObject("Case")
        trxnData = cPickle.dumps(objPair, 1)
        data.SetData(trxnData)

        dropSource = wx.DropSource(self)
        dropSource.SetData(data)
        result = dropSource.DoDragDrop(wx.Drag_AllowMove)
        if result == wx.DragMove:
            pass

class SingleCaseFrame(wx.Panel):
    def __init__(self, parent, package, transDescs, logFrame=None, transTimeOut=30, queueTimeOut=0.5):
        wx.Panel.__init__(self, parent, -1, size=(600,200))

        self._package = package
        self._transDescs = transDescs
        self._logFrame = logFrame
        self._currTrans = None

        self._button = wx.Button(self, 1003, "Start")
        self.Bind(wx.EVT_BUTTON, self.OnStart, self._button)
        label = wx.StaticText(self, -1, "case: ")
        self._caseName = wx.Choice(self, -1, size=(400,-1))
#        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF-8')
#        locale.setlocale(locale.LC_COLLATE, 'chinese-simplified')
#        locale.setlocale(locale.LC_ALL, 'chinese-simplified')
        locale.setlocale(locale.LC_ALL, '')
        sortedTransDescs = sorted(transDescs, cmp=locale.strcoll, key=lambda td: td.desc)
        for transDesc in sortedTransDescs:
#            self._caseName.Append(transDesc.name, transDesc)
            self._caseName.Append(transDesc.desc, transDesc)
        self.Bind(wx.EVT_CHOICE, self.OnEvtChoice, self._caseName)

        space = 4
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(label, 0, space)
        hsizer.Add(self._caseName, 0, space)
        hsizer.Add((20,20))
        hsizer.Add(self._button, 0, space)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self._scrollFrame = ScrolledFrame(self, -1, size=(600, 200))

        line = wx.StaticLine(self, -1, size=(500,-1), style=wx.LI_HORIZONTAL)

        tID = wx.NewId()
        self._list = TrxnListCtrl(self, tID, size=(500,-1), style=wx.LC_REPORT)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(hsizer, 0, space)
        bsizer.Add(self._scrollFrame, wx.GROW | wx.ALL, space)
        bsizer.Add(line, 0, space)
        bsizer.Add((space, space))
        bsizer.Add(self._list, wx.GROW | wx.ALL, space)
        self.SetSizer(bsizer)
        self.SetAutoLayout(True)
        wx.EVT_CLOSE(self, self.OnCloseWindow)

        self._sizer = bsizer
        self._switch = None
        self._msgLog = None
        self.queue = Queue.Queue()
        self.transTimeOut = transTimeOut
        self.queueTimeOut = queueTimeOut

        self.transThread = TransactionThread(self)
        self.transThread.start()


    def OnCloseWindow(self, event):
        self.transThread.quit()
#        self.Destroy()
#        event.Skip()

    def setTransDesc(self, transDesc):
        self._currTrans = transDesc
        self._scrollFrame.setTransDesc(self._package, transDesc)

    def setSwitch(self, switch):
        self._switch = switch

    def setMsgLog(self, msglog):
        self._msgLog = msgLog

    def OnEvtChoice(self, event):
        cb = event.GetEventObject()
        transDesc = cb.GetClientData(cb.GetSelection())
        self.setTransDesc(transDesc)

    def OnStart(self, event):
        self._button.Disable()
        self.transThread.setSendEvent()

    def OnSize(self, event):
#        w,h = self.GetClientSizeTuple()
#        self._list.SetDimensions(0, 0, w, h)
        event.Skip()

    def addMessage(self, message):
        self.queue.put(message, timeout=self.queueTimeOut)

    def unpackHeader(self, message):
        offset = 0
        meta = [('org',12), ('version',6), ('trans_type',1), ('message_type',1), ('direction',1), ('trans_code',6),('channel',2),('request_yymmdd',8),('request_time',14),('request_sn',20),('aic_time',14),('aic_yymmdd',8),('aic_sn',20),('branch',12),('operator',12),('node',13),('resp_code',4),('resp_desc',100),('mac',16),('reserved',30)]
        for (fd,sz) in meta: 
            message[0]

    def doTransaction(self):
        # should be only called from transaction thread
        transObj = self._scrollFrame.formTransObj()
        rquestMsg = self._package.pack(self._scrollFrame.transDesc, transObj)

        # for aic message header
        now = datetime.datetime.now
        #timestamp = ("%d%d%d%d%d%d%06d" % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond))
        #header = ("%12.12s" % Configure.config['org']) + ("%6.6s" % Configure.config['version']) + '0' + '0' + '0' + '999999' + '  ' + time.strftime("%Y%m%d") + time.strftime("%Y%m%d%H%M%S') + timestamp + (' ' * 42) + ("%12.12s" % Configure.config['branch']) + ("%12.12s" % Configure.config['operator']) + (' ' * 13) + (' ' * 4) + (' ' * 100) + (' ' * 16) + (' ' * 30)

        # log outgoing message
        log = dumpBinary(rquestMsg)
        wx.CallAfter(self._logFrame.addOutgoingMessage, log)
        (dummy,log) = self._package.unpack(self._currTrans._fielddef, rquestMsg)
        wx.CallAfter(self._logFrame.addOutgoingMessage, log)

        # sending the message out
        if (self._switch == None):
            self._button.Enable()
            print "must open connection first"
            return
        self._switch.addMessage(rquestMsg, Switch.NORMAL_TRXN)

        t_start = time.time()
        rcvObj = None
        while self.transThread.active:
            t = time.time()
            if (t - t_start > self.transTimeOut):
                break
            try:
                responseMsg = self.queue.get(timeout=self.queueTimeOut)
                log = dumpBinary(responseMsg)
                wx.CallAfter(self._logFrame.addIncomingMessage, log)
                (rcvObj, log) = self._package.unpack(self._currTrans._fielddef, responseMsg)
                wx.CallAfter(self._logFrame.addIncomingMessage, log)
                break        # got message, break the loop
            except:        # will get empty exception when timeout
                continue

        wx.CallAfter(self._list.InsertTrxn, self._scrollFrame.transDesc.name, transObj, rcvObj)
        wx.CallAfter(self._button.Enable)





if (__name__ == "__main__"):
    import IsoFieldDef
    fielddef = IsoFieldDef.LoadIsoFieldDef("project/cup/CupFieldDef.xml")
    config = {}
    config['pinblock_mode'] = "08"
    config['zpk'] = "1C25E98F9B9249AB"
    config['zak'] = "04C7BA865EECA85E"
    from TransactionDesc import CreateTransDescObject
    transDescs = []
    transDesc = CreateTransDescObject(fielddef, "project/cup/trans_cases/Reversal.xml", config)
    transDescs.append(transDesc)
    transDesc = CreateTransDescObject(fielddef, "project/cup/trans_cases/Sale.xml", config)
    transDescs.append(transDesc)

    print transDesc
    print transDesc.name

    theApp = wx.App(0)
    frame = wx.Frame(None, -1, "aaaaa")
    frame.Show(True)
    win = SingleCaseFrame(frame, transDescs)
    theApp.SetTopWindow(frame)
    theApp.MainLoop()

