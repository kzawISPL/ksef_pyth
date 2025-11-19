import os
import unittest

from sdk.ksefsdk import KSEFSDK


def _testdatadir(filexml: str) -> str:
    dir = os.path.join(os.path.dirname(__file__), "testdata")
    return os.path.join(dir, filexml)


class TestKsef(unittest.TestCase):

    _TOKEN = "20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370"
    _NIP = "7497725064"

    @classmethod
    def setUpClass(cls):
        cls.ksef = KSEFSDK.initsdk(
            what=KSEFSDK.DEVKSEF, nip=cls._NIP, token=cls._TOKEN)

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
        path = _testdatadir("FA_3_Przykład_9.xml")
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
