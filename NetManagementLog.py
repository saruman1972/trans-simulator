#!/usr/bin/python
# -*- coding: utf8 -*-

import wx

class NetStatusPanel(wx.Panel):
    def __init__(self, parent, id, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id)
        self.panel = wx.Panel(self, -1, wx.DLG_PNT(self, wx.Point(0, 0)), self.GetClientSize())
#        self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '宋体')
        self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self.panel, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
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




class NetManagementWin(wx.Frame):

    def __init__(self, parent, title="", size=wx.DefaultSize):
        wx.Frame.__init__(self, parent)
        self.SetTitle(title)

        self.splitter = wx.SplitterWindow(self, size=size)
        self.sendMsgLog = NetStatusPanel(self.splitter, -1)
        self.recvMsgLog = NetStatusPanel(self.splitter, -1)
        self.splitter.SplitHorizontally(self.recvMsgLog, self.sendMsgLog)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCloseWindow(self, event):
        return
        
    def OnSize(self, event):
        size = self.GetClientSize()
        self.splitter.SetSize(size)

    def OnClearLog(self, event):
        self.Text.Clear()

    def addIncomingMessage(self, message):
        self.recvMsgLog.addMsg(message)
        
    def addOutgoingMessage(self, message):
        self.sendMsgLog.addMsg(message)



if (__name__ == "__main__"):
    theApp = wx.App(0)
    win1 = NetStatusWin(None, "win1")
    win1.Show(True)
    win2 = NetStatusWin(None, "win2")
    win2.Show(True)
    win1.setTip("aaaaa")
    win2.setTip("bbbbb")
    theApp.MainLoop()

