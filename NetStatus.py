
import wx

class NetStatusWin(wx.Frame):

    def __init__(self, parent, title=""):
        wx.Frame.__init__(self, parent)

        self.SetTitle(title)
#        self.Text = wx.TextCtrl(self.panel, -1, "", wx.DLG_PNT(self, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        self.Text = wx.TextCtrl(self, -1, "", wx.DLG_PNT(self, wx.Point(0,0)), wx.Size(0,0), wx.TE_AUTO_URL | wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.button = wx.Button(self, 1003, "Clear Log")
        self.button.SetPosition((0, -20))
        self.msgBox = wx.StaticText(self, -1, "                          ", (0,0))
        self.Bind(wx.EVT_BUTTON, self.OnClearLog, self.button)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def OnCloseWindow(self, event):
        return

    def OnSize(self, event):
        size = self.GetClientSize()
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


if (__name__ == "__main__"):
    theApp = wx.App(0)
    win1 = NetStatusWin(None, "win1")
    win1.Show(True)
    win2 = NetStatusWin(None, "win2")
    win2.Show(True)
    win1.setTip("aaaaa")
    win2.setTip("bbbbb")
    theApp.MainLoop()
