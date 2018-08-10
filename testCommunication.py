import string
from socket import *
from binascii import *
import time
from Communication import *
from Security import *

pik_reset_msg = unhexlify("303030333435303030313034393939393920202020202020393939393939202020202020303030303030303030312020323031343038313620202020313332202020202020202020203030322020202020303030302020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020203030303030303030303035303938334138382020202020202020202020202020202020202020202020207c303832307c7c7c7c7c7c303831353233303335337c7c7c7c3931313935397c7c7c7c303831367c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c3230327c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c36353339343230307c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c7c")

def clientDemo(ip, port, message):
    sndSocket = socket(AF_INET, SOCK_STREAM)
    connectOk = False
    sndSocket.connect((ip, port))
    while True:
        lenstr = "%04d" % (len(message))
        sndSocket.send(lenstr)
        sndSocket.send(message)
        head = sndSocket.recv(4)
        if (head == ""):
            print "got nothing"
            break
        msgLen = ord(head[0])*256 + ord(head[1])
        msg = sndSocket.recv(msgLen)
        print "response=" + msg
        print "press <q> to quit, others continue"
        key = raw_input()
        if ((key == 'q') or (key == 'Q')):
            break
    sndSocket.close()
    pass

def serverDemo(port):
    s = socket(AF_INET, SOCK_STREAM)
#    s.bind((gethostbyname(gethostname()), port))
    s.bind(('', port))
    s.listen(1)        # only 1 connection permited simultaneously

    timeout = 1.0                # timeout = 1sec
    while True:
        (rcvSocket, addressInfo) = s.accept()
        print "connected at ", addressInfo
#        while True:
        if True:
            head = rcvSocket.recv(4)
#            if (head == ""):
#                print "got nothing"
#                break
            msgLen = string.atoi(head)
            message = rcvSocket.recv(msgLen)
            nbytes = len(message)
            print "got message:\n", message
#            b007 = message[20:30]
#            b011 = message[30:36]
#            b053 = message[36:52]
#            b070 = message[52:55]
#            b100_len = string.atoi(message[55:57])
#            b100 = message[55:(57+b100_len)]
#            b128 = message[(57+b100_len):]
#            mb = "0810" + " " + b007 + " " + b011 + " " + "00" + " " + b053 + " " + b070 + " " + b100
#            zmk = pyDes.triple_des(unhexlify("11111111111111111111111111111111"))
#            if b053[1] == '6':
#                new_key = unhexlify("1234567890ABCDEF1234567890ABCDEF")
#                k = pyDes.triple_des(new_key)
#                cv = k.encrypt("\0\0\0\0\0\0\0\0")
#                mac = calcMac(new_key, mb)
#                mac = mac + cv[:4]
#                b048 = "016" + zmk.encrypt(new_key)
#                b096 = unhexlify("0000000000000000")
#                message = "0810" + unhexlify("82200000020108000400000110000001") + b007 + b011 + "00" + b048 + b053 + b070 + b096 + b100 + mac
#            else:
#                new_key = unhexlify("1234567890ABCDEF")
#                k = pyDes.des(new_key)
#                cv = k.encrypt("\0\0\0\0\0\0\0\0")
#                mac = calcMac(new_key, mb)
#                mac = mac + cv[:4]
#                b096 = zmk.encrypt(new_key)
#                message = "0810" + unhexlify("82200000020008000400000110000001") + b007 + b011 + "00" + b053 + b070 + b096 + b100 + mac
            message = message[:48] + '1' + message[49:]
            head = "%04d" % len(message)
            print "send message:\n", (head+message)
            rcvSocket.send(head+message)
        rcvSocket.close()
#        break
    s.close()
    pass

#zmk = pyDes.triple_des(unhexlify("11111111111111111111111111111111"))
#new_key = "1234567890ABCDEF"
#b096 = zmk.encrypt(unhexlify(new_key))
#print hexlify(b096)
#sys.exit(0)
#message = '0820' + unhexlify('02200000020008000400000100000000') + '1201010101' + '000001' + '00' + '1000000000000000' + '101' + unhexlify('F8A030D99E479F11') + '0812345678'
#head = "%04d" % len(message)
#print "send message:\n", hexlify(head+message)
#print message[20:30]
#print message[30:36]
#clientDemo("127.0.0.1", 8888, pik_reset_msg)
serverDemo(8888)

