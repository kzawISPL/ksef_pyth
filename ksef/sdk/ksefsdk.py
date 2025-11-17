import logging
from time import sleep

import requests

from .encrypt import (
    encrypt_token, get_key_and_iv,
    encrypt_symmetric_key, to_base64,
    encrypt_invoice, calculate_hash
)


class KSEFSDK:

    _base_url = "https://ksef-test.mf.gov.pl/api/v2/"
    # _token = "20251108-EC-24C7EAF000-FC42E257A6-41|nip-7497725064|fad169115b1e482cb4ff38718d1d676dfa1f819060df4752b534391ea4a0d594"
    _token = "20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370"
    _nip = "7497725064"

    _SESSIONT = 5
    _INVOICET = 10

    def __init__(self):
        self._challenge, self._timestamp = self._get_challengeandtimestamp()
        self._kseftoken_certificate, self._symmetrickey_certificate = self._get_public_certificate()
        self._encrypted_token = encrypt_token(
            kseftoken=self._token,
            timestamp=self._timestamp,
            public_certificate=self._kseftoken_certificate
        )
        self._referencenumber, self._authenticationtoken = self._auth_ksef_token()
        self._session_status()
        self._access_token, self._refresh_token = self._redeem_token()
        self._symmetric_key, self._iv = get_key_and_iv()
        self._sessionreferencenumber = ''
        self._sessioninvoicereferencenumber = ''

    @property
    def challenge(self) -> str:
        return self._challenge

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def _construct_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    def _hook(self, endpoint: str, post: bool = True, dele: bool = False,
              body: dict = None, withbearer: bool = False, withbeareraccess: bool = False) -> dict:
        if withbearer or withbeareraccess:
            headers = {
                "Authorization": f"Bearer {self._access_token if withbeareraccess else self._authenticationtoken}"
            }
        else:
            headers = {}

        url = self._construct_url(endpoint=endpoint)
        logging.info(url)
        if dele:
            response = requests.delete(url, headers=headers)
        elif post:
            response = requests.post(url, json=body or {}, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response.json() if response.status_code != 204 else {}

    def _get_challengeandtimestamp(self) -> tuple[str, str]:
        response = self._hook("auth/challenge")
        return response["challenge"], response["timestamp"]

    def _get_public_certificate(self) -> tuple[str, str]:
        response = self._hook(
            "security/public-key-certificates", post=False)
        kseftoken_certificate = next(
            e['certificate'] for e in response if 'KsefTokenEncryption' in e['usage'])
        symmetrickey_certificate = next(
            e['certificate'] for e in response if 'SymmetricKeyEncryption' in e['usage'])
        return kseftoken_certificate, symmetrickey_certificate

    def _auth_ksef_token(self) -> tuple[str, str]:
        context = {
            "type:": "Nip",
            "value": self._nip
        }
        body = {
            "contextIdentifier": context,
            "challenge": self._challenge,
            "encryptedToken": self._encrypted_token
        }
        response = self._hook("auth/ksef-token", body=body)
        referenceNumber = response["referenceNumber"]
        token = response["authenticationToken"]["token"]
        return referenceNumber, token

    def _session_status(self) -> None:
        url = f"auth/{self._referencenumber}"
        for _ in range(self._SESSIONT):
            response = self._hook(url, post=False, withbearer=True)
            status = response["status"]["code"]
            description = response["status"]["description"]
            if status == 100:
                sleep(5)
            elif status == 200:
                return
            else:
                raise ValueError(
                    f"Session activation failed: {status} - {description}")

        raise TimeoutError("Session activation timed out.")

    def _redeem_token(self) -> tuple[str, str]:
        response = self._hook(endpoint="auth/token/redeem", withbearer=True)
        access_token = response["accessToken"]["token"]
        refresh_token = response["refreshToken"]["token"]
        return access_token, refresh_token

    def session_terminate(self) -> None:
        url = f"auth/sessions/{self._referencenumber}"
        self._hook(url, post=False, dele=True,
                   withbearer=True, withbeareraccess=True)

    def close_session(self) -> None:
        url = f"sessions/online/{self._sessionreferencenumber}/close"
        self._hook(url, withbeareraccess=True)

    def start_session(self) -> None:
        encrypted_symmetric_key = encrypt_symmetric_key(
            symmetricy_key=self._symmetric_key,
            public_certificate=self._symmetrickey_certificate
        )
        request_data = {
            "formCode": {
                "systemCode": "FA (3)",
                "schemaVersion": "1-0E",
                "value": "FA"
            },
            "encryption": {
                "encryptedSymmetricKey": to_base64(encrypted_symmetric_key),
                "initializationVector": to_base64(self._iv)
            },
        }
        response = self._hook(endpoint="sessions/online",
                              body=request_data, withbeareraccess=True)
        self._sessionreferencenumber = response["referenceNumber"]

    def _invoice_status(self) -> tuple[bool, str, str]:
        end_point = f'sessions/{self._sessionreferencenumber}/invoices/{self._sessioninvoicereferencenumber}'
        sleep_time = 2
        for _ in range(self._INVOICET):
            response = self._hook(endpoint=end_point,
                                  post=False, withbeareraccess=True)
            print(response)
            code = response["status"]["code"]
            if code == 100 or code == 150:
                sleep(sleep_time)
                sleep_time += 2
                continue
            return code == 200, response["status"]["description"], response["ksefNumber"] if code == 200 else ""
        return False, "Przekroczona liczba prób przetwarzania", ""

    def send_invoice(self, invoice: str) -> tuple[bool, str, str]:
        encrypted_invoice = encrypt_invoice(
            symmetric_key=self._symmetric_key, iv=self._iv, public_certificate=None, invoice=invoice)
        invoice_hash = calculate_hash(invoice)
        encrypted_invoice_hash = calculate_hash(encrypted_invoice)
        request_data = {
            "invoiceHash": invoice_hash,
            "invoiceSize": len(invoice),
            "encryptedInvoiceHash": encrypted_invoice_hash,
            "encryptedInvoiceSize": len(encrypted_invoice),
            "encryptedInvoiceContent": to_base64(encrypted_invoice),
            "offlineMode": False,
        }
        end_point = f"sessions/online/{self._sessionreferencenumber}/invoices"
        response = self._hook(endpoint=end_point,
                              body=request_data, withbeareraccess=True)
        self._sessioninvoicereferencenumber = response["referenceNumber"]
        return self._invoice_status()
