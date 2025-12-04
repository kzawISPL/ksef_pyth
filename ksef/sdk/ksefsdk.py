import logging
from time import sleep

import requests

from .encrypt import (
    encrypt_token, get_key_and_iv,
    encrypt_symmetric_key, to_base64,
    encrypt_invoice, calculate_hash
)


def _getlogger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logFormatter = logging.Formatter("%(asctime)s %(message)s")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger


_logger = _getlogger()


def _l(info: str):
    _logger.info(info)


class KSEFSDK:

    DEVKSEF = 0
    PREKSEF = 1
    PRODKSEF = 2

    _METHODPOST = 0
    _METHODDEL = 1
    _METHODGET = 2

    _NOBEARER = 0
    _BEARERTOKEN = 1
    _BEARERACCESS = 2

    _env_dict = {
        DEVKSEF:    "https://ksef-test.mf.gov.pl/api/v2/",
        PREKSEF:    "https://ksef-demo.mf.gov.pl/api/v2/",
        PRODKSEF:   "https://ksef.mf.gov.pl/api/v2"
    }

    @classmethod
    def initsdk(cls, env: int, nip: str, token: str):
        if env not in KSEFSDK._env_dict:
            raise ValueError(
                "Niepoprawne środowisko, parametr env musi mieć wartość DEVKSEF, PREKSEF lub PRODKSEF")
        return cls(url=KSEFSDK._env_dict[env], nip=nip, token=token)

    _SESSIONT = 5
    _INVOICET = 10

    def __init__(self, url: str, nip: str, token: str):
        self._base_url = url
        self._nip = nip
        self._token = token
        self._challenge, self._timestamp = self._get_challengeandtimestamp()
        self._kseftoken_certificate, self._symmetrickey_certificate = self._get_public_certificate()
        self._encrypted_token = encrypt_token(
            kseftoken=self._token,
            timestamp=self._timestamp,
            public_certificate=self._kseftoken_certificate
        )
        self._referencenumber,        self._authenticationtoken = self._auth_ksef_token()
        self._session_status()
        self._access_token,        self._refresh_token = self._redeem_token()
        self._symmetric_key, self._iv = get_key_and_iv()
        self._sessionreferencenumber = ''
        self._sessioninvoicereferencenumber = ''
        self._invoicereferencenumber = ''

    def _construct_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    def _hook_response(self, endpoint: str, method: int = _METHODPOST, body: dict | None = None, bearer=_BEARERACCESS) -> requests.Response:
        if bearer != self._NOBEARER:
            headers = {
                "Authorization": f"Bearer {self._access_token if bearer == self._BEARERACCESS else self._authenticationtoken}"
            }
        else:
            headers = {}

        # print(f"body={body}")
        # print(f"headers={headers}")

        url = self._construct_url(endpoint=endpoint)
        _l(url)
        if method == self._METHODDEL:
            response = requests.delete(url, headers=headers)
        elif method == self._METHODPOST:
            response = requests.post(url, json=body or {}, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response

    def _hook(self, endpoint: str, method: int = _METHODPOST, body: dict | None = None, bearer: int = _BEARERACCESS) -> dict:

        response = self._hook_response(
            endpoint=endpoint, method=method, body=body, bearer=bearer)
        return response.json() if response.status_code != 204 else {}

    def _get_challengeandtimestamp(self) -> tuple[str, str]:
        response = self._hook("auth/challenge", bearer=self._NOBEARER)
        return response["challenge"], response["timestamp"]

    def _get_public_certificate(self) -> tuple[str, str]:
        response = self._hook(
            "security/public-key-certificates", method=self._METHODGET, bearer=self._NOBEARER)
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
        response = self._hook("auth/ksef-token", body=body, bearer=self._NOBEARER)
        referenceNumber = response["referenceNumber"]
        token = response["authenticationToken"]["token"]
        return referenceNumber, token

    def _session_status(self) -> None:
        url = f"auth/{self._referencenumber}"
        for _ in range(self._SESSIONT):
            response = self._hook(
                url, method=self._METHODGET, bearer=self._BEARERTOKEN)
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
        response = self._hook(endpoint="auth/token/redeem",bearer=self._BEARERTOKEN)
        access_token = response["accessToken"]["token"]
        refresh_token = response["refreshToken"]["token"]
        return access_token, refresh_token

    def session_terminate(self) -> None:
        url = f"auth/sessions/{self._referencenumber}"
        self._hook(url, method=self._METHODDEL)

    def close_session(self) -> None:
        url = f"sessions/online/{self._sessionreferencenumber}/close"
        self._hook(url)

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
        response = self._hook(endpoint="sessions/online", body=request_data)
        self._sessionreferencenumber = response["referenceNumber"]

    def _invoice_status(self) -> tuple[bool, str, str]:
        end_point = f'sessions/{self._sessionreferencenumber}/invoices/{self._sessioninvoicereferencenumber}'
        sleep_time = 2
        for no in range(self._INVOICET):
            response = self._hook(endpoint=end_point, method=self._METHODGET)
            code = response["status"]["code"]
            # stworz komunikat
            description = response["status"]["description"]
            details = response["status"].get("details")
            if isinstance(details, list):
                description += (" " + " ".join(details))

            # czy w trakcie przetwarzania
            if code == 100 or code == 150:
                _l(description)
                _l(f"Próba {no+1}, max {self._INVOICET}, czekam {sleep_time} sekund")
                sleep(sleep_time)
                sleep_time += 2
                # spróbuj jeszcze raz
                continue
            # albo jest poprawnie albo błąd
            if code == 200:
                self._invoicereferencenumber = response["referenceNumber"]
                return True, description, response["ksefNumber"]
            return False, description, ""

        return False, "Przekroczona liczba prób przetwarzania", ""

    def send_invoice(self, invoice: str) -> tuple[bool, str, str]:
        invoice_len, encrypted_invoice = encrypt_invoice(
            symmetric_key=self._symmetric_key, iv=self._iv, invoice=invoice)
        invoice_hash = calculate_hash(invoice)
        encrypted_invoice_hash = calculate_hash(encrypted_invoice)
        request_data = {
            "invoiceHash": invoice_hash,
            "invoiceSize": invoice_len,
            "encryptedInvoiceHash": encrypted_invoice_hash,
            "encryptedInvoiceSize": len(encrypted_invoice),
            "encryptedInvoiceContent": to_base64(encrypted_invoice),
            "offlineMode": False,
        }
        end_point = f"sessions/online/{self._sessionreferencenumber}/invoices"
        response = self._hook(endpoint=end_point, body=request_data)
        self._sessioninvoicereferencenumber = response["referenceNumber"]
        return self._invoice_status()

    def pobierz_upo(self) -> str:
        end_point = f"sessions/{self._sessionreferencenumber}/invoices/{self._invoicereferencenumber}/upo"
        response = self._hook_response(endpoint=end_point, method=self._METHODGET)
        return response.text
    

    def search_incoming_invoices(self):
        end_point = f"invoices/query/metadata"
        payload =   {
                                "subjectType": "Subject2",
                                "dateRange": {
                                "dateType": "PermanentStorage",
                                "from": "2024-01-01T09:22:13.388+00:00",
                                "to": "2025-12-30T09:24:13.388+00:00"
                                },
                                "currencyCodes": [
                                "PLN",
                                "EUR"
                                ]
                        }
        response = self._hook(endpoint=end_point, body=payload, bearer=self._BEARERACCESS)
        return response
