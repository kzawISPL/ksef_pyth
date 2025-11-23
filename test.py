from ksef import KSEFSDK
from ksef import KONWDOKUMENT
from tests import test_mix as T
import datetime


def KS():
    K = KSEFSDK.initsdk(KSEFSDK.DEVKSEF, nip=T.NIP, token=T.TOKEN)
    return K


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def gen_numer_faktry():
    nr = "FV"
    data_f = datetime.datetime.now().isoformat()
    return nr + data_f


def test1():
    K = KS()
    # print(K.challenge, K.timestamp)
    K.start_session()
    K.close_session()
    K.session_terminate()


def test2():
    K = KS()
    K.start_session()
#    path = KONWDOKUMENT.zrob_dokument_xml(zmienne={})
    path = T.testdatadir("FA_3_Przykład_9.xml")
    print(path)
    with open(path, "r") as f:
        invoice = f.read()
    status = K.send_invoice(invoice=invoice)
    print(status)
    K.close_session()
    K.session_terminate()


def test3():
    inpath = T.testdatadir("FA_3_Przykład_9_pattern.xml")
    outpath = T.workdatadir("faktura.xml")
    zmienne = {
        KONWDOKUMENT.DATA_WYSTAWIENIA: _today(),
        KONWDOKUMENT.NIP: T.NIP,
        KONWDOKUMENT.NIP_NABYWCA: T.NIP_NABYWCA,
        KONWDOKUMENT.NUMER_FAKTURY: gen_numer_faktry()
    }
    KONWDOKUMENT.konwertuj(sou=inpath, dest=outpath, zmienne=zmienne)


if __name__ == "__main__":
    # test2()
    test1()
    # test3()
