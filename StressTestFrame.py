from lxml import etree
import threading
import  sys
import  cPickle
import  wx
import time
import Queue
from ScrolledFrame import ScrolledFrame
import  wx.lib.mixins.listctrl  as  listmix
from Switch import Switch
from DumpBinary import dumpBinary
import string
import re
import random
import IsoFieldDef


class CaseConfig:

    def __init__(self):
        self.name = ""
        self.rate = 100
        self.amountLow = 0
        self.amountHigh = 99999999
        self.currencyCode = "random"
        self.pinPresentRate = 100
        self.pinCorrectRate = 100
        self.mccSetting = ""
        self.mcc = []
        self.rand = random.Random()

        self.allMCC = [
            "5811",
            "5812",
            "5813",
            "5814",
            "3501",
            "3502",
            "3503",
            "3504",
            "3505",
            "3506",
            "3507",
            "3508",
            "3509",
            "3510",
            "3511",
            "3512",
            "3513",
            "3514",
            "3515",
            "3516",
            "3517",
            "3518",
            "3519",
            "3520",
            "3521",
            "3522",
            "3523",
            "3524",
            "3525",
            "3526",
            "3527",
            "3528",
            "3529",
            "3530",
            "3531",
            "3533",
            "3532",
            "3534",
            "3535",
            "3536",
            "3537",
            "3538",
            "3539",
            "3540",
            "3541",
            "3542",
            "3543",
            "3544",
            "3545",
            "3546",
            "3548",
            "3549",
            "3550",
            "3551",
            "3552",
            "3553",
            "3555",
            "3558",
            "3554",
            "3561",
            "3556",
            "3562",
            "3557",
            "3563",
            "3564",
            "3559",
            "3565",
            "3560",
            "3568",
            "3570",
            "3572",
            "3573",
            "3574",
            "3575",
            "3566",
            "3577",
            "3567",
            "3579",
            "3581",
            "3569",
            "3582",
            "3583",
            "3571",
            "3584",
            "3585",
            "3586",
            "3587",
            "3588",
            "3576",
            "3590",
            "3591",
            "3578",
            "3592",
            "3593",
            "3580",
            "3595",
            "3598",
            "3599",
            "3603",
            "3612",
            "3615",
            "3589",
            "3620",
            "3622",
            "3623",
            "3624",
            "3625",
            "3594",
            "3628",
            "3629",
            "3596",
            "3631",
            "3597",
            "3632",
            "3633",
            "3634",
            "3602",
            "3635",
            "3636",
            "3604",
            "3637",
            "3607",
            "3638",
            "3639",
            "3640",
            "3641",
            "3642",
            "3643",
            "3644",
            "3645",
            "3646",
            "3647",
            "3648",
            "3649",
            "3650",
            "3651",
            "3652",
            "3653",
            "3654",
            "3655",
            "3656",
            "3657",
            "3658",
            "3659",
            "3660",
            "3661",
            "3662",
            "3663",
            "3664",
            "3665",
            "3666",
            "3667",
            "3668",
            "3669",
            "3670",
            "3671",
            "3672",
            "3673",
            "3674",
            "3675",
            "3676",
            "3677",
            "3678",
            "3679",
            "3680",
            "3681",
            "3682",
            "3683",
            "3684",
            "3685",
            "3686",
            "3687",
            "3688",
            "3689",
            "3690",
            "3691",
            "3692",
            "3693",
            "3694",
            "3695",
            "3696",
            "3697",
            "3698",
            "3699",
            "3700",
            "3701",
            "3702",
            "3703",
            "3704",
            "3705",
            "3706",
            "3707",
            "3708",
            "3709",
            "3710",
            "3711",
            "3712",
            "3713",
            "3714",
            "3715",
            "3716",
            "3717",
            "3718",
            "3719",
            "3720",
            "3721",
            "3722",
            "3723",
            "3724",
            "3725",
            "3726",
            "3727",
            "3728",
            "3729",
            "3730",
            "3731",
            "3732",
            "3733",
            "3734",
            "3735",
            "3736",
            "3737",
            "3738",
            "3739",
            "3740",
            "3741",
            "3742",
            "3743",
            "3744",
            "3745",
            "3746",
            "3747",
            "3748",
            "3749",
            "3750",
            "3751",
            "3752",
            "3753",
            "3754",
            "3755",
            "3756",
            "3757",
            "3758",
            "3759",
            "3760",
            "3761",
            "3762",
            "3763",
            "3764",
            "3765",
            "3766",
            "3767",
            "3768",
            "3769",
            "3770",
            "3771",
            "3772",
            "3773",
            "3774",
            "3775",
            "3776",
            "3777",
            "3778",
            "3779",
            "3780",
            "3781",
            "3782",
            "3783",
            "3784",
            "3785",
            "3786",
            "3787",
            "3788",
            "3789",
            "3790",
            "3791",
            "3792",
            "3794",
            "3795",
            "7011",
            "3793",
            "3796",
            "3797",
            "3798",
            "3799",
            "5722",
            "7011",
            "3000",
            "3001",
            "3002",
            "3003",
            "3004",
            "3005",
            "3006",
            "3007",
            "3008",
            "3009",
            "3010",
            "3011",
            "3012",
            "3013",
            "3014",
            "3015",
            "3016",
            "3017",
            "3018",
            "3020",
            "3021",
            "3022",
            "3023",
            "3024",
            "3025",
            "3026",
            "3027",
            "3028",
            "3029",
            "3030",
            "3031",
            "3032",
            "3033",
            "3034",
            "3035",
            "3036",
            "3037",
            "3038",
            "3039",
            "3040",
            "3041",
            "3042",
            "3043",
            "3044",
            "3045",
            "3046",
            "3047",
            "3048",
            "3049",
            "3050",
            "3051",
            "3052",
            "3053",
            "3054",
            "3055",
            "3056",
            "3057",
            "3058",
            "3060",
            "3061",
            "3063",
            "3064",
            "3065",
            "3066",
            "3067",
            "3071",
            "3075",
            "3076",
            "3077",
            "3078",
            "3081",
            "3082",
            "3083",
            "3084",
            "3085",
            "3086",
            "3087",
            "3088",
            "3089",
            "3090",
            "3092",
            "3094",
            "3095",
            "3096",
            "3097",
            "3098",
            "3099",
            "3100",
            "3102",
            "3103",
            "3106",
            "3110",
            "3111",
            "3112",
            "3115",
            "3117",
            "3118",
            "3125",
            "3126",
            "3127",
            "3129",
            "3130",
            "3132",
            "3133",
            "3135",
            "3136",
            "3137",
            "3138",
            "3143",
            "3144",
            "3145",
            "3146",
            "3148",
            "3151",
            "3154",
            "3156",
            "3159",
            "3161",
            "3164",
            "3165",
            "3167",
            "3170",
            "3171",
            "3172",
            "3174",
            "3175",
            "3176",
            "3177",
            "3178",
            "3180",
            "3181",
            "3182",
            "3183",
            "3184",
            "3185",
            "3186",
            "3187",
            "3190",
            "3191",
            "3192",
            "3193",
            "3196",
            "3197",
            "3200",
            "3203",
            "3204",
            "3206",
            "3211",
            "3212",
            "3215",
            "3216",
            "3217",
            "3218",
            "3219",
            "3220",
            "3221",
            "3222",
            "3223",
            "3228",
            "3229",
            "3231",
            "3233",
            "3234",
            "3235",
            "3238",
            "3239",
            "3240",
            "3241",
            "3242",
            "3243",
            "3251",
            "3252",
            "3253",
            "3254",
            "3256",
            "3259",
            "3261",
            "3262",
            "3263",
            "3266",
            "3267",
            "3280",
            "3282",
            "3284",
            "3285",
            "3286",
            "3287",
            "3292",
            "3293",
            "3294",
            "3295",
            "3297",
            "3298",
            "3299",
            "4511",
            "3079",
            "3131",
            "3188",
            "3213",
            "3226",
            "3236",
            "3245",
            "3246",
            "3247",
            "3248",
            "3260",
            "4011",
            "4111",
            "4112",
            "4131",
            "4214",
            "4784",
            "4789",
            "4121",
            "3351",
            "3352",
            "3353",
            "3354",
            "3357",
            "3359",
            "3360",
            "3361",
            "3362",
            "3364",
            "3366",
            "3368",
            "3370",
            "3374",
            "3376",
            "3380",
            "3381",
            "3385",
            "3386",
            "3387",
            "3388",
            "3389",
            "3390",
            "3391",
            "3393",
            "3394",
            "3395",
            "3396",
            "3398",
            "3400",
            "3405",
            "3409",
            "3412",
            "3414",
            "3420",
            "3421",
            "3423",
            "3425",
            "3427",
            "3428",
            "3429",
            "3430",
            "3431",
            "3432",
            "3433",
            "3434",
            "3435",
            "3436",
            "3437",
            "3438",
            "3439",
            "3441",
            "7512",
            "7513",
            "7519",
            "3355",
            "4411",
            "4722",
            "4723",
            "4814",
            "4816",
            "4821",
            "5960",
            "5962",
            "5964",
            "5965",
            "5966",
            "5967",
            "5968",
            "5969",
            "4813",
            "4119",
            "5975",
            "5976",
            "8011",
            "8021",
            "8031",
            "8041",
            "8042",
            "8043",
            "8044",
            "8049",
            "8050",
            "8062",
            "8071",
            "8099",
            "8111",
            "8211",
            "8220",
            "8241",
            "8244",
            "8249",
            "8299",
            "8351",
            "5944",
            "5094",
            "5993",
            "1520",
            "5998",
            "5271",
            "5511",
            "5521",
            "5592",
            "5598",
            "5599",
            "5561",
            "9999",
        ]

    def initRandomSeed(self):
        self.pinPresentPercent = []
        for i in range(self.pinPresentRate-1):
            self.pinPresentPercent.append(True)
        for j in range(100-self.pinPresentRate+1):
            self.pinPresentPercent.append(False)

        self.pinCorrectPercent = []
        for i in range(self.pinCorrectRate-1):
            self.pinCorrectPercent.append(True)
        for j in range(100-self.pinCorrectRate+1):
            self.pinCorrectPercent.append(False)

        if self.mccSetting == "random":
            self.mcc = self.allMCC
        else:
            self.mcc = self.mccSetting.split(' ')

    def genAmount(self):
        amount = self.rand.randint(self.amountLow, self.amountHigh)
        amount = (amount / 100) * 100
        return amount

    def genCurrencyCode(self):
        if (self.currencyCode == "random"):
            return self.rand.choice(["156", "840"])
        else:
            return self.currencyCode

    def hasPIN(self):
        pinPresent = self.rand.choice(self.pinPresentPercent)
        return pinPresent

    def genPIN(self, orgPIN):
        pinCorrect = self.rand.choice(self.pinCorrectPercent)
        if pinCorrect:
            PIN = orgPIN
        else:
            PIN = '000000'
        return PIN

    def genMCC(self):
        preDefined = self.rand.choice([True, False])
        if preDefined:
            return self.rand.choice(self.mcc)
        else:
            return "%04d" % self.rand.randint(1000,9999)



def LoadCase(node):
    case = CaseConfig()
    case.name = node.attrib['name']
    if node.attrib.has_key('rate'):
        case.rate = string.atoi(re.sub("%", "", node.attrib['rate']))

    for elem in node.getchildren():
        if elem.tag == "amount":
            if elem.attrib.has_key('high'):
                case.amountHigh = string.atoi(elem.attrib['high'])
            if elem.attrib.has_key('low'):
                case.amountLow = string.atoi(elem.attrib['low'])
        elif elem.tag == "currency_code":
                case.currencyCode = elem.attrib['value']
        elif elem.tag == "mcc":
            case.mccSetting = elem.attrib['value']
        elif elem.tag == "pin":
            if elem.attrib.has_key('present_rate'):
                case.pinPresentRate = string.atoi(elem.attrib['present_rate'])
            if elem.attrib.has_key('correct_rate'):
                case.pinCorrectRate = string.atoi(elem.attrib['correct_rate'])
    return case

def AdjustCaseRate(cases):
    total = 0
    for case in cases:
        total += case.rate
        case.initRandomSeed()
    for case in cases:
        case.rate = case.rate * 100 / total

def LoadCaseConfig(filename):
    """ load the stress test case config from file """

    doc = etree.parse(filename)
    root = doc.getroot()
    cases = []
    for elem in root.xpath("case"):
        cases.append(LoadCase(elem))

    AdjustCaseRate(cases)
    return cases


class Card:

    def __init__(self):
        self.index = -1
        self.cardno = ""
        self.track2 = ""
        self.pin = ""


def LoadCardList(filename):
    cards = []
    file = open(filename, 'r')
    blank = re.compile(r"^$")
    comment = re.compile(r"^#")
    for line in file.xreadlines():
        info = string.strip(line)
        if (blank.match(info) or comment.match(info)):continue
        (index,cardno,track2,pin) = string.split(info, '|')
        card = Card()
        card.index = index
        card.cardno = cardno
        card.track2 = track2
        card.pin = pin
        cards.append(card)
    file.close()
    return cards








class SendThread(threading.Thread):

    def __init__(self, frame, timeout=0.5):
        threading.Thread.__init__(self)
        self.frame = frame
        self.active = True
        self.timeout = timeout
        self.rand = random.Random()
        self.percent = []
        index = 0
        for case in self.frame._caseList.cases:
            for i in range(case.rate): self.percent.append(index)
            index += 1

    def quit(self):
        self.active = False

    def run(self):
        while (self.active):
            caseIndex = self.rand.choice(self.percent)
            case = self.frame._caseList.cases[caseIndex]
            card = self.rand.choice(self.frame._cardList.cards)
            print case.name, card.cardno
            self.frame.doTransaction(case, card)
            time.sleep(0.05)


class ReceiveThread(threading.Thread):

    def __init__(self, frame, timeout=0.5):
        threading.Thread.__init__(self)
        self.frame = frame
        self.active = True
        self.timeout = timeout

    def quit(self):
        self.active = False

    def run(self):
        self.queueTimeOut = 5
        while self.active:
            try:
                message = self.frame.queue.get(timeout=self.queueTimeOut)
                print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
                log = dumpBinary(message)
                self.frame._logFrame.addIncomingMessage(log)
                (rcvObj, log) = frame._package.unpack(IsoFieldDef.GlobalIsoFieldDef, message)
                self.frame._logFrame.addIncomingMessage(log)
                # could do some statistic here
            except Queue.Empty:        # will get empty exception when timeout
                continue



class CaseListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Populate()
        listmix.TextEditMixin.__init__(self)

        self.cases = []
        self.FillCaseConfig()

    def Populate(self):
        self.InsertColumn(0, "name")
        self.InsertColumn(1, "rate")
        self.InsertColumn(2, "amount low")
        self.InsertColumn(3, "amount high")
        self.InsertColumn(4, "currency code")
        self.InsertColumn(5, "pin present rate")
        self.InsertColumn(6, "pin correct rate")
        self.InsertColumn(7, "mcc")

    def InsertTrxn(self, name, caseConfig):
        item = self.InsertStringItem(sys.maxint, name)
        self.SetStringItem(item, 0, name)
        self.SetStringItem(item, 1, "%d" % caseConfig.rate)
        self.SetStringItem(item, 2, "%d" % caseConfig.amountLow)
        self.SetStringItem(item, 3, "%d" % caseConfig.amountHigh)
        self.SetStringItem(item, 4, caseConfig.currencyCode)
        self.SetStringItem(item, 5, "%d" % caseConfig.pinPresentRate)
        self.SetStringItem(item, 6, "%d" % caseConfig.pinCorrectRate)
        self.SetStringItem(item, 7, caseConfig.mccSetting)

    def FillCaseConfig(self):
        self.cases = LoadCaseConfig('StressTestConfigure.xml')
        for caseConfig in self.cases:
            self.InsertTrxn(caseConfig.name, caseConfig)



class CardListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.Populate()
        listmix.TextEditMixin.__init__(self)

        self.cards = LoadCardList('cards.txt')
        self.FillCardList(self.cards)

    def Populate(self):
        self.InsertColumn(0, "index")
        self.InsertColumn(1, "card no")
        self.InsertColumn(2, "track2")
        self.InsertColumn(3, "pin")

    def FillCardList(self, cards):
        for card in cards:
            item = self.InsertStringItem(sys.maxint, card.cardno)
            self.SetStringItem(item, 0, card.index)
            self.SetStringItem(item, 1, card.cardno)
            self.SetStringItem(item, 2, card.track2)
            self.SetStringItem(item, 3, card.pin)



class StressTestFrame(wx.Panel):
    def __init__(self, parent, package, transDescs, logFrame=None, transTimeOut=30, queueTimeOut=0.5):
        wx.Panel.__init__(self, parent, -1, size=(500,200))

        self._package = package
        self._transDescs = transDescs
        self._logFrame = logFrame
        self._currTrans = None

        labelCase = wx.StaticText(self, -1, "case config: ")
        tID = wx.NewId()
        self._caseList = CaseListCtrl(self, tID, size=(500,-1), style=wx.LC_REPORT)

        line = wx.StaticLine(self, -1, size=(500,-1), style=wx.LI_HORIZONTAL)

        labelCard = wx.StaticText(self, -1, "card list: ")
        tID = wx.NewId()
        self._cardList = CardListCtrl(self, tID, size=(500,-1), style=wx.LC_REPORT)

        self._startButton = wx.Button(self, 1003, "Start")
        self.Bind(wx.EVT_BUTTON, self.OnStart, self._startButton)
        self._status = 0

        space = 4
        self.Bind(wx.EVT_SIZE, self.OnSize)

        bsizer = wx.BoxSizer(wx.VERTICAL)
        bsizer.Add(labelCase, 0, space)
        bsizer.Add(self._caseList, wx.GROW | wx.ALL, space)
        bsizer.Add(line, 0, space)
        bsizer.Add((space, space))
        bsizer.Add(labelCard, 0, space)
        bsizer.Add(self._cardList, wx.GROW | wx.ALL, space)
        bsizer.Add(self._startButton, 0, space)
        self.SetSizer(bsizer)
        self.SetAutoLayout(True)
        wx.EVT_CLOSE(self, self.OnCloseWindow)

        self._sizer = bsizer
        self._switch = None
        self._msgLog = None
        self.queue = Queue.Queue()
        self.transTimeOut = transTimeOut
        self.queueTimeOut = queueTimeOut

        self.initCaseMap(transDescs)
        self.sendThread = None
        self.receiveThread = None


    def initCaseMap(self, transDescs):
        self.caseMap = {}
        for transDesc in transDescs:
            self.caseMap[transDesc.name] = transDesc


    def OnCloseWindow(self, event):
        if (self.sendThread != None):
            self.sendThread.quit()
        if (self.receiveThread != None):
            self.receiveThread.quit()

#        self.Destroy()
#        event.Skip()

    def setSwitch(self, switch):
        self._switch = switch

    def setMsgLog(self, msglog):
        self._msgLog = msgLog

    def OnStart(self, event):
        if (self._status == 0):
#            if (self._switch == None):
#                print "must open connection first"
#                return
            self._status = 1
            title = "stop"
            self.sendThread = SendThread(self)
            self.sendThread.start()
            self.receiveThread = ReceiveThread(self)
            self.receiveThread.start()

        else:
            self._status = 0
            self.receiveThread.quit()
            self.sendThread.quit()
            title = "start"
        self._startButton.SetLabel(title)

    def OnSize(self, event):
#        w,h = self.GetClientSizeTuple()
#        self._list.SetDimensions(0, 0, w, h)
        event.Skip()

    def addMessage(self, message):
        self.queue.put(message, timeout=self.queueTimeOut)

    def formTransObj(self, case, card):
        transDesc = self.caseMap[case.name]

        transObj = {}
        try:
            transDesc._fields[2].value = card.cardno
        except: pass
        try:
            amount = case.genAmount()
            transDesc._fields[4].value = "%012d" % amount
            print "amount=",transDesc._fields[4].value,
        except: pass
        try:
            transDesc._fields[18].value = case.genMCC()
            print "mcc=",transDesc._fields[18].value,
        except: pass
        try:
            transDesc._fields[35].value = card.track2
        except: pass
        try:
            transDesc._fields[49].value = case.genCurrencyCode()
        except: pass
        try:
            PIN = case.genPIN(card.pin)
            transDesc._fields[52].value = PIN
            print "pin=",transDesc._fields[52].value,
        except: pass
        print "\n"

        indexes = transDesc._fields.keys()
        indexes.sort()
        for index in indexes:
            field = transDesc._fields[index]
            value = field.getValue(transObj)
            transObj[index] = {'host' : value}
        return transObj

    def doTransaction(self, case, card):
        transDesc = self.caseMap[case.name]
        transObj = self.formTransObj(case, card)
        msg = transDesc.pack(transObj)

        # log outgoing message
        log = dumpBinary(msg)
        wx.CallAfter(self._logFrame.addOutgoingMessage, log)
        (dummy,log) = self._package.unpack(transDesc._fielddef, msg)
        wx.CallAfter(self._logFrame.addOutgoingMessage, log)

        # sending the message out
#        self._switch.addMessage(msg, Switch.NORMAL_TRXN)





if (__name__ == "__main__"):
    import IsoFieldDef
    fielddef = IsoFieldDef.LoadIsoFieldDef("project/cup/CupFieldDef.xml")
    config = {}
    config['pinblock_mode'] = "08"
    config['zpk'] = "1C25E98F9B9249AB"
    config['zak'] = "04C7BA865EECA85E"
    from TransactionDesc import CreateTransDescObject
    transDescs = []
    transDesc = CreateTransDescObject(fielddef, "project/cup/trans_cases/Reversal.xml", config)
    transDescs.append(transDesc)
    transDesc = CreateTransDescObject(fielddef, "project/cup/trans_cases/Sale.xml", config)
    transDescs.append(transDesc)

    print transDesc
    print transDesc.name

    theApp = wx.App(0)
    frame = wx.Frame(None, -1, "aaaaa")
    frame.Show(True)
    win = SingleCaseFrame(frame, transDescs)
    theApp.SetTopWindow(frame)
    theApp.MainLoop()

