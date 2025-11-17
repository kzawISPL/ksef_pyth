from sdk import KSEFSDK
from sdk import KONWDOKUMENT


def test1():
    K = KSEFSDK()
    print(K.challenge, K.timestamp)
    K.start_session()
    K.close_session()
    K.session_terminate()


def test2():
    K = KSEFSDK()
    print(K.challenge, K.timestamp)
    K.start_session()
    path = KONWDOKUMENT.zrob_dokument_xml(zmienne={})
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
