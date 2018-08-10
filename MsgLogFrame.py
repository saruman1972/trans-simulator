#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
import wx

class MsgLogPanel(wx.Panel):
    def __init__(self, parent, id, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id)
        self.panel = wx.Panel(self, -1, wx.DLG_PNT(self, wx.Point(0, 0)), self.GetClientSize())
#        self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "宋体")
        self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.DefaultSize, wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.Text.SetFont(font)
        self.button = wx.Button(self.panel, 1003, "Clear Log")
        self.button.SetPosition((0, -20))
        self.msgBox = wx.StaticText(self.panel, -1, "", (0,0))
        self.Bind(wx.EVT_BUTTON, self.OnClearLog, self.button)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnCloseWindow(self, event):
        self.Destroy()
        event.Skip()

    def OnSize(self, event):
        size = self.GetClientSize()
        self.panel.SetSize(size)
        self.Text.SetSize((size.x, size.y-25))
        self.button.SetPosition((0, size.y-25))
        self.msgBox.SetPosition((100, size.y-25))
        self.msgBox.SetSize((size.x, 25))

    def OnClearLog(self, event):
        self.Text.Clear()

    def addMsg(self, msg):
        self.Text.AppendText(msg + "\n\n")

    def setTip(self, tip):
        self.msgBox.SetLabel(tip)

class MsgLogFrame(wx.Panel):

    def __init__(self, parent, id, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, size=size)
#        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        self.splitter = wx.SplitterWindow(self, size=size)
        self.recvMsgLog = MsgLogPanel(self.splitter, -1)
        self.sendMsgLog = MsgLogPanel(self.splitter, -1)
        self.splitter.SplitHorizontally(self.sendMsgLog, self.recvMsgLog)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        size = self.GetClientSize()
        self.splitter.SetSize(size)
        self.splitter.SetSashPosition(size.GetHeight()/2)

    def addIncomingMessage(self, message):
        self.recvMsgLog.addMsg(message)

    def addOutgoingMessage(self, message):
        self.sendMsgLog.addMsg(message)


if (__name__ == "__main__"):
    theApp = wx.App(0)
    frame = wx.Frame(None, -1, size=(200,200))
    win = MsgLogFrame(frame, -1)

    frame.Show(True)
    theApp.SetTopWindow(frame)
    theApp.MainLoop()

