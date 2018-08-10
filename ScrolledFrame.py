
import  cPickle
import  wx
import  wx.lib.scrolledpanel as scrolled
# from wxPython.wx import *
import string
import Communication
from TransactionDesc import *
from SubFieldDialog import SubFieldDialog
import IsoFieldDef
from MyChoices import MyChoices


class CaseDropTarget(wx.PyDropTarget):
    def __init__(self, window):
        wx.PyDropTarget.__init__(self)
        self._scrollFrame = window

        # specify the type of data we will accept
        self.data = wx.CustomDataObject("Case")
        self.SetDataObject(self.data)


    # some virtual methods that track the progress of the drag
    def OnEnter(self, x, y, d):
#        self.log.WriteText("OnEnter: %d, %d, %d\n" % (x, y, d))
        return d

    def OnLeave(self):
#        self.log.WriteText("OnLeave\n")
        pass

    def OnDrop(self, x, y):
#        self.log.WriteText("OnDrop: %d %d\n" % (x, y))
        return True

    def OnDragOver(self, x, y, d):
        #self.log.WriteText("OnDragOver: %d, %d, %d\n" % (x, y, d))

        # The value returned here tells the source what kind of visual
        # feedback to give.  For example, if wxDragCopy is returned then
        # only the copy cursor will be shown, even if the source allows
        # moves.  You can use the passed in (x,y) to determine what kind
        # of feedback to give.  In this case we return the suggested value
        # which is based on whether the Ctrl key is pressed.
        return d



    # Called when OnDrop returns True.  We need to get the data and
    # do something with it.
    def OnData(self, x, y, d):
#        self.log.WriteText("OnData: %d, %d, %d\n" % (x, y, d))

        # copy the data from the drag source to our data object
        if self.GetData():
            trxnData = self.data.GetData()
            (trxnObj,rcvObj) = cPickle.loads(trxnData)
            self._scrollFrame.fillTrxn(trxnObj, rcvObj)

        # what is returned signals the source what to do
        # with the original data (move, copy, etc.)  In this
        # case we just return the suggested value given to us.
        return d

class ScrolledFrame(scrolled.ScrolledPanel):
    def __init__(self, parent, ID, title="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):

        scrolled.ScrolledPanel.__init__(self, parent, -1, size=size, style=style)

        # facility for drag and drop
        dt = CaseDropTarget(self)
        self.SetDropTarget(dt)

    def layoutItems(self, sizer, fields):
        self.tcs = []
        self.btnTextMap = {}
        self.fieldTextMap = {}
        for field in fields:
            if (field.show == 0):
                continue

            label = wx.StaticText(self, -1, field.isofield.desc+":")
            if (field.isofield.valueOrigin.__class__ == IsoFieldDef.ValueOriginChoices):
                tc = MyChoices(self, -1, choices=field.isofield.valueOrigin.choices, size=(300,-1), style=wx.CB_DROPDOWN)
                tc.SetValue(field.value)
            else:
                tc = wx.TextCtrl(self, -1, field.value, size=(300,-1))
                tc.SetMaxLength(field.size)

            btn = wx.Button(self, 1004, "...", size=(20,20))
            self.Bind(wx.EVT_BUTTON, self.OnSubField, btn)
            sizer.Add(label, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
            sizer.Add(tc, flag=wx.RIGHT, border=10)
            sizer.Add(btn)

            self.tcs.append((field, tc))
            self.btnTextMap[btn] = (field, tc)
            self.fieldTextMap[field] = tc

    def setTransDesc(self, package, transDesc):
        self.DestroyChildren()
        self.package = package
        self.transDesc = transDesc
        fgs1 = wx.FlexGridSizer(cols=3, vgap=4, hgap=4)
        fields = []

        indexes = self.package._fields.keys()
        indexes.sort()
        for index in indexes:
            fields.append(self.package._fields[index])

        indexes = self.transDesc._fields.keys()
        indexes.sort()
        for index in indexes:
            fields.append(self.transDesc._fields[index])
        self.layoutItems(fgs1, fields)

        self.SetSizer( fgs1 )
        self.SetAutoLayout(1)
        self.SetupScrolling()

    def formTransObj(self):
        # first: fill the field value with values keyined
        for (field, tc) in self.tcs:
            field.value = tc.GetValue()

        transObj = {}
        # then get each field value to form the send object
        indexes = self.package._fields.keys()
        indexes.sort()
        for index in indexes:
            field = self.package._fields[index]
            value = field.getValue(transObj)
            transObj[index] = {'host' : value}

        indexes = self.transDesc._fields.keys()
        indexes.sort()
        for index in indexes:
            field = self.transDesc._fields[index]
            if len(field.copy_field_maps) == 0:    # leave the copied fields untouched
                value = field.getValue(transObj)
            else:
                value = field.value
            transObj[index] = {'host' : value}

        return transObj

    def fillTrxn(self, transObj, rcvObj):
        for (field, tc) in self.tcs:
            value = ""
            fieldDef = field.isofield
            if (field.copy_field_type == ""):    # normal field
                if len(field.copy_field_maps) > 0:    # copy from another fields
                    (original_field_type, original_field_index, target_field_name) = field.copy_field_maps[0]
                    if original_field_type == 'Response':
                        if (rcvObj != None) and rcvObj.has_key(original_field_index):
                            value = rcvObj[original_field_index]
                    else:
                        if transObj.has_key(original_field_index):
                            value = transObj[original_field_index]['host']
                else:    # copy from coresponding fields
                    if transObj.has_key(fieldDef.index):
                        value = transObj[fieldDef.index]['host']
                    elif (rcvObj != None) and rcvObj.has_key(fieldDef.index):
                        value = rcvObj[fieldDef.index]
                    value = fieldDef.valueOrigin.setValue(value, transObj)
            else:                                # compound field, copy from other fields
                if fieldDef.sub_fields.has_key(field.copy_field_type):
                    sub_field_type = fieldDef.sub_fields[field.copy_field_type]
                    for (original_field_type, original_field_index, target_field_name) in field.copy_field_maps:
                        sub_value = ""
                        if original_field_type == 'Response':
                            if (rcvObj != None) and rcvObj.has_key(original_field_index):
                                sub_value = rcvObj[original_field_index]
                        else:
                            if transObj.has_key(original_field_index):
                                sub_value = transObj[original_field_index]['host']
                        target_field = sub_field_type.fields_name_hash[target_field_name]
                        sub_value = target_field.fieldEnc.dopadding(sub_value, target_field.size)
                        value += sub_value
            field.value = value
            print "setValue:value=", value
            tc.SetValue(value)

    def OnSubField(self, event):
        """ for sub fields editing """
        transObj = self.formTransObj()

        btn = event.GetEventObject()
        (field, tc) = self.btnTextMap[btn]

        isofield = field.isofield
        if True:
#        try:
            sub_field_type = isofield.sub_fields[field.subfield_type]
            dlg = SubFieldDialog(self, field.value, field.subfield_type, sub_field_type, transObj)
            dlg.CenterOnScreen()
            val = dlg.ShowModal()
            if (val == wx.ID_OK):
                field.value = dlg.value
                tc.SetValue(dlg.value)
            dlg.Destroy()
#        except:
#            pass

if (__name__ == "__main__"):
    theApp = wx.App(0)
    import IsoFieldDef
    fielddef = IsoFieldDef.LoadIsoFieldDef("project/cup/CupFieldDef.xml")
    transDesc = CreateTransDescObject(fielddef, "project/cup/trans_cases/Reversal.xml", None)
    frame = wx.Frame(NULL, -1, "aaaaa")
    win = ScrolledFrame(frame, -1, size=(350,200), style=wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
    win.setTransDesc(transDesc)
    frame.Show(true)
    theApp.SetTopWindow(frame)
    theApp.MainLoop()

