import sys

import wx
#from wxPython.wx import *

class SettingDialog(wx.Dialog):
    def __init__(self, parent, title, config):
        self.config = config
        self.changed = False

        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        if self.config.has_key('remote'):
            label = wx.StaticText(self, -1, "remote host")
            sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            box = wx.BoxSizer(wx.HORIZONTAL)
    
            label = wx.StaticText(self, -1, "ip:")
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            
            self.textRemoteIP = wx.TextCtrl(self, -1, "", size=(80,-1))
            self.textRemoteIP.SetValue(self.config['remote']['ip']);
            box.Add(self.textRemoteIP, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
            box = wx.BoxSizer(wx.HORIZONTAL)
    
            label = wx.StaticText(self, -1, "port:")
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            self.textRemotePort = wx.TextCtrl(self, -1, "", size=(80,-1))
            self.textRemotePort.SetValue(str(self.config['remote']['port']));
            box.Add(self.textRemotePort, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        if self.config.has_key('remote') and self.config.has_key('local'):
            line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
            sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        if self.config.has_key('local'):
            label = wx.StaticText(self, -1, "local host")
            sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            box = wx.BoxSizer(wx.HORIZONTAL)
    
            label = wx.StaticText(self, -1, "port:")
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            self.textLocalPort = wx.TextCtrl(self, -1, "", size=(80,-1))
            self.textLocalPort.SetValue(str(self.config['local']['port']));
            box.Add(self.textLocalPort, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
    
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
            line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
            sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnSizer = wx.StdDialogButtonSizer()

        self.btnOK = wx.Button(self, wx.ID_OK)
        self.btnOK.SetDefault()
        btnSizer.AddButton(self.btnOK)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnSizer.AddButton(btn)
        btnSizer.Realize()

        sizer.Add(btnSizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.btnOK)

    def OnOK(self, event):
        if self.config.has_key('remote'):
            if (self.config['remote']['ip'] != self.textRemoteIP.GetValue()):
                self.config['remote']['ip'] = self.textRemoteIP.GetValue()
                self.changed = True
            if (self.config['remote']['port'] != int(self.textRemotePort.GetValue())):
                self.config['remote']['port'] = int(self.textRemotePort.GetValue())
                self.changed = True
        if self.config.has_key('local'):
            if (self.config['local']['port'] != int(self.textLocalPort.GetValue())):
                self.config['local']['port'] = int(self.textLocalPort.GetValue())
                self.changed = True
        self.EndModal(wx.ID_OK)

class TheApp(wx.App):
    def OnInit(self):
        config = {}
        config['remote'] = {}
        config['local'] = {}
        config['remote']['ip'] = "10.168.4.46"
        config['remote']['port'] = "10012"
        config['local']['port'] = "30012"
        dlg = SettingDialog(None, "Setting Dialog", config)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            print "ok pressed"
        dlg.Destroy()
        return false

if __name__ == "__main__":
        theApp = TheApp(0)
        theApp.MainLoop()
