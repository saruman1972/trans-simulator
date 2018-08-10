import sys
import wx
import Version

class AboutDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, Version.version)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, "Build Date:" + Version.builddate)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, "Copyright All in Finance")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, Version.warning)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, "Author:" + Version.author)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnOK = wx.Button(self, wx.ID_OK)
        btnOK.SetDefault()
        sizer.Add(btnOK, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

class TheApp(wx.App):
    def OnInit(self):
        dlg = AboutDialog(None, "Setting Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        dlg.Destroy()
        return False

if __name__ == "__main__":
        theApp = TheApp(0)
        theApp.MainLoop()
