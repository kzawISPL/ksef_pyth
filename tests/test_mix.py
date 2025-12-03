import datetime
import os
from ksef import KSEFSDK


# TOKEN="20251203-EC-1B54C8E000-E05CE637BC-3C|nip-5272527149|98b2bf56b5ac46a9b00e3dd81e6b9d6b5fca3001ce8d4d7a810d824ddb3ac790" token dla wersji TEST
TOKEN="20251203-EC-2CD52B1000-F5691FF4BF-87|nip-5272527149|bdd389512ed646c4a7b49577b5bd86765174c12d0ee544ae8ef0763cd4094358"    #token dla wersji DEMO
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
