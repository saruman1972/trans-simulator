import wx

class MyChoices(wx.ComboBox):
    
    def __init__(self, parent, id, value='', pos=wx.DefaultPosition, size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator, name=wx.ComboBoxNameStr):
        self.choices = choices
        ccs = []
        for (desc, val) in choices:
            if desc == '':
                ccs.append(val)
            else:
                ccs.append(desc)
        wx.ComboBox.__init__(self, parent, id, value, pos, size, ccs, style, validator, name)
    
    def SetValue(self, value):
        index = -1
        i = 0
        for (desc, val) in self.choices:
#            if (value == val) or (value == desc):
            if value == val:
                index = i
                self.SetSelection(index)
                return
            i = i+1
        if index == -1:
            wx.ComboBox.SetValue(self, value)
        
    def GetValue(self):
        index = self.GetSelection()
        if index == wx.NOT_FOUND:
            val = wx.ComboBox.GetValue(self)
        else:
            (dummy,val) = self.choices[index]
        return val
