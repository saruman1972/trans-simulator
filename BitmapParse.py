import sys
import wx
from binascii import *
from Security import *

class BitmapParseDialog(wx.Dialog):
    def __init__(self, parent, title):

        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, -1, "bit map:")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        self.bitmap = wx.TextCtrl(self, -1, "", size=(300,20))
        sizer.Add(self.bitmap, flag=wx.ALIGN_CENTER)
        
        self.bm_disp = wx.TextCtrl(self, -1, "", size=(300,100), style=wx.TE_MULTILINE)
        sizer.Add(self.bm_disp, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnOK = wx.Button(self, wx.ID_OK)
        self.btnOK.SetDefault()
        btnSizer.Add(self.btnOK)

        self.btnParse = wx.Button(self, 1001, "Parse")
        btnSizer.Add(self.btnParse)

        sizer.Add(btnSizer)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.btnOK)
        self.Bind(wx.EVT_BUTTON, self.OnParse, self.btnParse)
        
    def OnOK(self, event):
        self.EndModal(wx.ID_OK)

    def OnParse(self, event):
        bitmap = self.bitmap.GetValue()
        if ((len(bitmap) != 16) and (len(bitmap) != 32)):
            return
        result = self.getFields(bitmap)
        self.bm_disp.SetValue(result)
        
    def getFields(self, bitmap):
        """ input bitmap should be BCD """
        bitlist = String_to_BitList(unhexlify(bitmap))
        result = ""
        for i in range(len(bitlist)):
            if bitlist[i]:
                result += "%d, " % (i+1)
        if (len(result) > 0):
            result = result[:-2]
        return result

if __name__ == "__main__":
        theApp = wx.App(0)
        dlg = BitmapParseDialog(None, "Bitmap Parse Dialog")
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            print "ok pressed"
        dlg.Destroy()
        theApp.MainLoop()
