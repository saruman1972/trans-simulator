import sys
import wx

class OpenProjectDialog(wx.Dialog):
    def __init__(self, parent, title, projects):
        wx.Dialog.__init__(self, parent, -1, title)
        
        self.projects = projects
        self.theProject = None
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Available Projects:")
        sizer.Add(label)
        self.list = wx.ListBox(self, size=(500,200), choices=projects)
        sizer.Add(self.list)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.EvtListBoxDClick, self.list)

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

    def EvtListBoxDClick(self, event):
        index = self.list.GetSelection()
        if index != -1:
            self.theProject = self.projects[index]
            self.EndModal(wx.ID_OK)
        
    def OnOK(self, event):
        index = self.list.GetSelection()
        if index == -1:
            return
        self.theProject = self.projects[index]
        self.EndModal(wx.ID_OK)

def openProject(path):
    from ListFile import listFiles
    
    projects = listFiles(path, '*.prj', recurse=0)
    projects.sort()
    dlg = OpenProjectDialog(None, "Open Project", projects)
    dlg.CenterOnScreen()
    val = dlg.ShowModal()
    if (val == wx.ID_OK):
        pass
    dlg.Destroy()
    return dlg.theProject

if __name__ == "__main__":
    theApp = wx.App(0)
    from os.path import *
    aaaa = abspath('project')
    print aaaa
    print dirname(aaaa)
    theProject = openProject('project')
    print theProject
    theApp.MainLoop()
