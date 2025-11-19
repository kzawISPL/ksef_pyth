import os
from sdk import KSEFSDK
# from sdk import KONWDOKUMENT

_TOKEN = "20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370"
_NIP = "7497725064"


def KS():
    K = KSEFSDK.initsdk(KSEFSDK.DEVKSEF, nip=_NIP, token=_TOKEN)
    return K


def _testdatadir(filexml: str) -> str:
    dir = os.path.join(os.path.dirname(__file__), "tests", "testdata")
    return os.path.join(dir, filexml)


def test1():
    K = KS()
    print(K.challenge, K.timestamp)
    K.start_session()
    K.close_session()
    K.session_terminate()


def test2():
    K = KS()
    K.start_session()
#    path = KONWDOKUMENT.zrob_dokument_xml(zmienne={})
    path = _testdatadir("FA_3_Przykład_9.xml")
    print(path)
    with open(path, "r") as f:
        invoice = f.read()
    status = K.send_invoice(invoice=invoice)
    print(status)
    K.close_session()
    K.session_terminate()


if __name__ == "__main__":
    test2()
    # test1()
