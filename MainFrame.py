import sys

#from wxPython.wx import *
import wx
import threading

from StressTestFrame import StressTestFrame
from SingleCaseFrame import SingleCaseFrame
from MsgLogFrame import MsgLogFrame
import IsoFieldDef
from TransactionDesc import *
from Configure import *
from Switch import Switch

from SettingDialog import SettingDialog
from AboutDialog import AboutDialog
from ListFile import listFiles
import Version
from Dictionary import LoadDictionaries

doingStressTest = False

class MainFrame(wx.Frame):
    def __init__(self, parent, title, theProject, fielddef, config, package, transDescs):
        self.theProject = theProject
        self.config = config
        self.fielddef = fielddef
        self.package = package
        self.transDescs = transDescs
        self.switch = None
        self.splitter = None
        self.configChanged = False

        wx.Frame.__init__(self, parent, -1, title, wx.Point(200, 200), wx.Size(800, 600))
        wx.EVT_SIZE(self, self.OnSize)
        self.Menubar = wx.MenuBar(wx.MB_DOCKABLE)
        wx.EVT_MENU(self, 0x201, self.OnMenuClose)
        wx.EVT_MENU(self, 0x203, self.OnMenuConnect)
        wx.EVT_MENU(self, 0x204, self.OnMenuDisconnect)
        wx.EVT_MENU(self, 0x205, self.OnMenuSetting)
        wx.EVT_MENU(self, 0x206, self.OnMenuHelp)

        FileMenu = wx.Menu("", wx.MENU_TEAROFF)
        FileMenu.Append(0x201, "Exit", "")
        self.Menubar.Append(FileMenu, "File")
        MngMenu = wx.Menu("", wx.MENU_TEAROFF)
        MngMenu.Append(0x203, "Open Connection", "")
        MngMenu.Append(0x204, "Close Connection", "")
        MngMenu.Append(0x205, "Setting", "")
        self.Menubar.Append(MngMenu, "Managment")
        HelpMenu = wx.Menu("", wx.MENU_TEAROFF)
        HelpMenu.Append(0x206, "About")
        self.Menubar.Append(HelpMenu, "Help")
        self.SetMenuBar(self.Menubar)

        self.splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        if doingStressTest:
            self.dataFrame = StressTestFrame(self.splitter, self.package, self.transDescs)
        else:
            self.dataFrame = SingleCaseFrame(self.splitter, self.package, self.transDescs)
        self.logFrame = MsgLogFrame(self.splitter, -1)
        self.splitter.SplitVertically(self.dataFrame, self.logFrame, 550)
        self.dataFrame._logFrame = self.logFrame

        wx.EVT_CLOSE(self, self.OnCloseWindow)

        icon = wx.Icon('icons/Simulator.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)


    def OnCloseWindow(self, event):
        if self.configChanged:
            SaveConfiguration(self.theProject, self.config)
        if (self.switch != None):
            self.switch.quit()

        self.dataFrame.OnCloseWindow(event)
        self.Destroy()
        event.Skip()

    def OnSize(self, event):
        size = self.GetClientSize()
        if (self.splitter != None):
            self.splitter.SetSize(size)
        event.Skip()

    def OnMenuClose(self, event):
        self.Close()
        event.Skip()

    def OnMenuOpen(self, event):
        dlg = wx.FileDialog(self)
        btn = dlg.ShowModal()
        if (btn == wx.ID_OK):
            filename = dlg.GetPath()
            self.transDesc = CreateTransDescObject(self.fields, filename, self.config)
            self.dataFrame.setTransDesc(self.transDesc)
            self.config['case'] = filename
        return

    def OnMenuConnect(self, event):
        if (self.switch == None):
            self.switch = Switch(self.config, self.fielddef, self.package)
            self.switch.online()
            self.dataFrame.setSwitch(self.switch)
            self.switch.setTransactionThread(self.dataFrame)

    def OnMenuDisconnect(self, event):
        if (self.switch != None):
            self.switch.quit()
            self.switch = None
            self.dataFrame.setSwitch(None)

    def OnMenuSetting(self, event):
        dlg = SettingDialog(self, "Setting Dialog", self.config)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if (val == wx.ID_OK):
            if dlg.changed:
                self.config = dlg.config
                self.configChanged = true
        dlg.Destroy()

    def OnMenuHelp(self, event):
        dlg = AboutDialog(self, "About")
        dlg.CenterOnScreen()
        dlg.ShowModal()
        dlg.Destroy()

def LoadTransactions(path, fielddef, config):
    transDescs = []
    cases = listFiles(path, '*.xml', recurse=0)
    for case in cases:
        transDesc = CreateTransDescObject(fielddef, case, config)
        transDescs.append(transDesc)
    return transDescs

def LoadPackageHeader(path, fielddef, config):
    transDescs = []
    headers = listFiles(path, 'PackageHeader.xml', recurse=0)

    if len(headers) == 1:
        package = CreateTransDescObject(fielddef, headers[0], config)
    else:
        package = Package(fielddef, config)
    return package

def showMsg(msg):
        dlg = wx.MessageDialog(None, msg, 'message box', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

class TheApp(wx.App):
    def OnInit(self):
        from OpenProjectDialog import openProject
        from os.path import abspath,dirname,basename

        projectPath = 'project'
        theProject = openProject(projectPath)
        if theProject == None:
            return True

        fullpath = abspath(theProject)
        dirpath = dirname(fullpath)
        config = LoadConfiguration(theProject)
        dicts = LoadDictionaries(dirpath+'/'+config['dictionary_path'])
        fielddef = IsoFieldDef.LoadIsoFieldDef(dirpath+'/'+config['field_def'], dicts)
        isofile = dirpath+'/'+config['field_def']
        package = LoadPackageHeader(dirname(isofile), fielddef, config)
        transDescs = LoadTransactions(dirpath+'/'+config['transaction_cases_path'], fielddef, config)
        managementDescs = LoadTransactions(dirpath+'/'+config['management_cases_path'], fielddef, config)
        config['management_cases'] = managementDescs

        frame = MainFrame(None, Version.version + ' -- ' + config['name'], theProject, fielddef, config, package, transDescs)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True




if (__name__ == "__main__"):
    import getopt
#    global doingStressTest
    doingStressTest = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s", ["stress_test"])
    except getopt.GetoptError:
        opts = ()
    for (opt, arg) in opts:
        if opt in ("-s", "--stress_test"):
            doingStressTest = True
    theApp = TheApp(0)
    theApp.MainLoop()

