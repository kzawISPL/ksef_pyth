import unittest

from ksef import KSEFSDK, KONWDOKUMENT
from tests import test_mix as T


class TestKsef(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # cls.ksef = KSEFSDK.initsdk(
        #    what=KSEFSDK.DEVKSEF, nip=T.NIP, token=T.TOKEN)
        cls.ksef = T.KS()

    @classmethod
    def tearDownClass(cls):
        cls.ksef.session_terminate()

    def test_init_and_terminate(self):
        pass

    def test_start_and_close_online(self):
        self.ksef.start_session()
        self.ksef.close_session()

    def test_send_incorrect_invoice(self):
        self.ksef.start_session()
        path = T.testdatadir("FA_3_Przykład_9.xml")
        print(path)
        with open(path, "r") as f:
            invoice = f.read()
        status = self.ksef.send_invoice(invoice=invoice)
        print(status)
        ok, description, _ = status
        self.assertFalse(ok)
        self.assertIn(
            "Błąd weryfikacji semantyki dokumentu faktury", description)

        self.ksef.close_session()

    def test_konwertuj_plik(self):
        inpath = T.testdatadir("FA_3_Przykład_9_pattern.xml")
        outpath = T.workdatadir("faktura.xml")
        zmienne = {
            KONWDOKUMENT.DATA_WYSTAWIENIA: T.today(),
            KONWDOKUMENT.NIP: T.NIP,
            KONWDOKUMENT.NIP_NABYWCA: T.NIP_NABYWCA,
            KONWDOKUMENT.NUMER_FAKTURY: T.gen_numer_faktry()
        }
        KONWDOKUMENT.konwertuj(sou=inpath, dest=outpath, zmienne=zmienne)
        # odczytaj skonwertowany plik
        with open(outpath, "r") as f:
            invoice = f.read()
        self.assertIn(T.NIP, invoice)
        self.assertIn(T.NIP_NABYWCA, invoice)
