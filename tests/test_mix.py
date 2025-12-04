import datetime
import os
from ksef import KSEFSDK


# TOKEN="20251203-EC-" token dla wersji TEST
TOKEN="20251203"    #token dla wersji DEMO
NIP = "5272527149"
NIP_NABYWCA = "7952809480"

def testdatadir(filexml: str) -> str:
    dir = os.path.join(os.path.dirname(__file__), "testdata")
    return os.path.join(dir, filexml)


def workdatadir(filexml: str) -> str:
    dir = os.path.join(os.path.dirname(__file__), "worktemp")
    if not os.path.isdir(dir):
        os.mkdir(dir)
    return os.path.join(dir, filexml)


def KS():
    K = KSEFSDK.initsdk(KSEFSDK.DEVKSEF, nip=NIP, token=TOKEN)
    return K


def today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def gen_numer_faktry():
    nr = "FV"
    data_f = datetime.datetime.now().isoformat()
    return nr + data_f
