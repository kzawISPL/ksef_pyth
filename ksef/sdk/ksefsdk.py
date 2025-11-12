import requests
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import datetime
import calendar
from time import sleep


def _encrypt_token(kseftoken: str, timestamp: str, public_certificate: str) -> str:
    t = datetime.datetime.fromisoformat(timestamp)
    t = int((calendar.timegm(t.timetuple()) * 1000) + (t.microsecond / 1000))
    token = f"{kseftoken}|{t}".encode('utf-8')

    crt = f'-----BEGIN CERTIFICATE-----\n{public_certificate}\n-----END CERTIFICATE-----'

    certificate = x509.load_pem_x509_certificate(
        crt.encode("utf-8")
    )
    public_key = certificate.public_key()
    encrypted = public_key.encrypt(
        token,
        padding=padding.PKCS1v15()
    )
    return base64.b64encode(encrypted).decode("utf-8")


class KSEFSDK:

    _base_url = "https://ksef-test.mf.gov.pl/api/v2/"
    _token = "20251108-EC-24C7EAF000-FC42E257A6-41|nip-7497725064|fad169115b1e482cb4ff38718d1d676dfa1f819060df4752b534391ea4a0d594"
    _nip = "7497725064"

    _SESSIONT = 5

    def __init__(self):
        self._challenge, self._timestamp = self._get_challengeandtimestamp()
        self._public_certificate = self._get_public_certificate()
        self._encrypted_token = _encrypt_token(
            kseftoken=self._token,
            timestamp=self._timestamp,
            public_certificate=self._public_certificate
        )
        self._referencenumber, self._authenticationtoken = self._auth_ksef_token()
        self._session_status()

    @property
    def challenge(self) -> str:
        return self._challenge

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def _construct_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    def _hook(self, endpoint: str, post: bool = True, body: dict = None, withbearer: bool = False) -> dict:
        if withbearer:
            headers = {
                "Authorization": f"Bearer {self._authenticationtoken}"
            }
        else:
            headers = {}

        url = self._construct_url(endpoint=endpoint)
        response = requests.post(
            url, json=body or {}, headers=headers) if post else requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _get_challengeandtimestamp(self) -> tuple[str, str]:
        response = self._hook("auth/challenge")
        return response["challenge"], response["timestamp"]

    def _get_public_certificate(self) -> str:
        response = self._hook("security/public-key-certificates", post=False)
        return response[0]["certificate"]

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
            else:
                raise ValueError(f"Session activation failed: {status} - {description}")

        raise TimeoutError("Session activation timed out.")
