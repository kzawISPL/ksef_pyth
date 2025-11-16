from sdk import KSEFSDK
from sdk import KONWDOKUMENT


def test1():
    K = KSEFSDK()
    print(K.challenge, K.timestamp)
    #K.session_terminate()
    K.start_session()


def test2():
    path = KONWDOKUMENT.zrob_dokument_xml(zmienne={})
    print(path)


if __name__ == "__main__":
    #test2()
    test1()
