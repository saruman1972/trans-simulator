import sys
import re
import wx
import IsoFieldDef
from MyChoices import MyChoices

class SubFieldDialog(wx.Dialog):
    def __init__(self, parent, value, title, subfields, transObj):
        if re.match("^ *$", value):
            self.value = ""
        else:
            self.value = value
        print "len=", len(self.value)
        self.subfields = subfields
        self.transObj = transObj

        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.LayoutFields(subfields, sizer)

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
        self.value = ""
        for (isofield,tc) in self.tcs:
            value = tc.GetValue()
            value = isofield.valueOrigin.getValue(value, self.transObj)
            (value, dummy) = isofield.encode(value)
            self.value += value
        self.EndModal(wx.ID_OK)

    def LayoutFields(self, subfields, sizer):
        self.tcs = []
        index = 0

        hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(hor_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        col = (len(subfields.fields_array)-1) / 10 + 1
        row = 0
        cur_sizer = None
        for isofield in subfields.fields_array:
            if row % 10 == 0:
                cur_sizer = wx.BoxSizer(wx.VERTICAL)
                hor_sizer.Add(cur_sizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
            row = row + 1

            field_value = self.value[index:index+isofield.size]
            (field_value, dummy) = isofield.decode(field_value)
            field_value = isofield.valueOrigin.setValue(field_value, self.transObj)
            index = index + isofield.size
            label = wx.StaticText(self, -1, isofield.name)
            if (isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginChoices):
                tc = MyChoices(self, -1, choices=isofield.valueOrigin.choices, size=(80,-1), style=wx.CB_DROPDOWN)
            else:
                tc = wx.TextCtrl(self, -1, "", size=(80,-1))
                if isofield.disp_size > 0:
                    tc.SetMaxLength(isofield.disp_size)
                else:
                    tc.SetMaxLength(isofield.size)
            tc.SetValue(field_value)
            self.tcs.append((isofield, tc))

            box = wx.BoxSizer(wx.HORIZONTAL)
            box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box.Add(tc, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
            cur_sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)


if __name__ == "__main__":
    from MainFrame import LoadDictionaries
    dicts = LoadDictionaries("project/cup/dictionary")
#    dicts = LoadDictionaries("project/jccf/dictionary")
    theApp = wx.App(0)
    import IsoFieldDef
    fielddef = IsoFieldDef.LoadIsoFieldDef("project/cup/CupFieldDef.xml", dicts)
#    fielddef = IsoFieldDef.LoadIsoFieldDef("project/jccf/JccfFieldDef.xml", dicts)
    fields = fielddef.getFieldsIndexHash()
#    field90 = fields[90]
#    subfield_type = "Original Data Elements"
#    subfields = field90.sub_fields[subfield_type]
#    dlg = SubFieldDialog(None, "020007631309071927010000102100000001021000", subfield_type, subfields.fields_array)
#    field48 = fields[48]
#    subfield_type = "Loyal Points Redemption"
#    subfield_type = "Merchandise information"
#    subfields = field48.sub_fields[subfield_type]
    field55 = fields[55]
    subfield_type = "Request"
    subfields = field55.sub_fields[subfield_type]
    dlg = SubFieldDialog(None, "", subfield_type, subfields, None)
    dlg.CenterOnScreen()
    val = dlg.ShowModal()
    if (val == wx.ID_OK):
        print "ok pressed"
        print dlg.value
    dlg.Destroy()
    theApp.MainLoop()
