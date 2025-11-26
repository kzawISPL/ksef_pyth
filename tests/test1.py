from typing import Callable
import unittest

from ksef import KONWDOKUMENT
from tests import test_mix as T
import xml.etree.ElementTree as et


class TestKsef(unittest.TestCase):

    # ---------------------
    # helpers
    # ---------------------
    def _prepare_invoice(self) -> str:
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
        return invoice

    def _wyslij_ksef(self, invoice: str, action: Callable | None = None) -> tuple[bool, str, str]:
        self.ksef.start_session()
        status = self.ksef.send_invoice(invoice=invoice)
        print(status)
        if action is not None:
            action()
        self.ksef.close_session()
        return status

    # ---------------------
    # test fixture
    # ---------------------

    @classmethod
    def setUpClass(cls):
        cls.ksef = T.KS()

    @classmethod
    def tearDownClass(cls):
        cls.ksef.session_terminate()

    # -------------------
    # test suite
    # -------------------

    def test_init_and_terminate(self):
        pass

    def test_start_and_close_online(self):
        self.ksef.start_session()
        self.ksef.close_session()

    def test_send_incorrect_invoice(self):
        path = T.testdatadir("FA_3_Przykład_9.xml")
        print(path)
        with open(path, "r") as f:
            invoice = f.read()
        status = self._wyslij_ksef(invoice=invoice)
        print(status)
        ok, description, _ = status
        self.assertFalse(ok)
        self.assertIn(
            "Błąd weryfikacji semantyki dokumentu faktury", description)

    def test_konwertuj_plik(self):
        self._prepare_invoice()

    def test_wyslij_do_ksef(self):
        invoice = self._prepare_invoice()
        status = self._wyslij_ksef(invoice=invoice)
        print(status)
        ok, description, numerksef = status
        self.assertTrue(ok)
        self.assertEqual("Sukces", description)
        self.assertNotEqual("", numerksef)

    def test_wyslij_do_ksef_i_wez_upo(self):

        def wez_upo():
            upo = self.ksef.pobierz_ufo()
            print(upo)
            # sprawdz, czy plik xml
            # wyrzuci błąd, jeśli nie jest poprawny xml
            tree = et.fromstring(upo)

        invoice = self._prepare_invoice()
        status = self._wyslij_ksef(invoice=invoice, action=wez_upo)
        ok, description, numerksef = status
        self.assertTrue(ok)
        self.assertEqual("Sukces", description)
        self.assertNotEqual("", numerksef)
