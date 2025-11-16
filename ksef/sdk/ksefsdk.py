import requests
from time import sleep
from .encrypt import (
    encrypt_token, get_key_and_iv,
    encrypt_symmetric_key, to_base64
)


class KSEFSDK:

    _base_url = "https://ksef-test.mf.gov.pl/api/v2/"
    #_token = "20251108-EC-24C7EAF000-FC42E257A6-41|nip-7497725064|fad169115b1e482cb4ff38718d1d676dfa1f819060df4752b534391ea4a0d594"
    _token = "20251116-EC-0317C65000-2CA83C40D9-73|nip-7497725064|80be6cfced7f44eb860aeeb644e8cffdd59bbad9e218415296db90a39e6e5370"
    #_token = "XXXXXX"
    _nip = "7497725064"

    _SESSIONT = 5

    def __init__(self):
        self._challenge, self._timestamp = self._get_challengeandtimestamp()
        self._public_certificate = self._get_public_certificate()
        self._encrypted_token = encrypt_token(
            kseftoken=self._token,
            timestamp=self._timestamp,
            public_certificate=self._public_certificate
        )
        self._referencenumber, self._authenticationtoken = self._auth_ksef_token()
        # self._session_status()
        self._symmetric_key, self._iv = get_key_and_iv()

    @property
    def challenge(self) -> str:
        return self._challenge

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def _construct_url(self, endpoint: str) -> str:
        return f"{self._base_url}{endpoint}"

    def _hook(self, endpoint: str, post: bool = True, dele: bool = False, body: dict = None, withbearer: bool = False) -> dict:
        if withbearer:
            headers = {
                "Authorization": f"Bearer {self._authenticationtoken}"
            }
        else:
            headers = {}

        url = self._construct_url(endpoint=endpoint)
        if dele:
            response = requests.delete(url, headers=headers)
        elif post:
            response = requests.post(url, json=body or {}, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()

        return response.json()

    def _get_challengeandtimestamp(self) -> tuple[str, str]:
        response = self._hook("auth/challenge")
        return response["challenge"], response["timestamp"]

    def _get_public_certificate(self) -> str:
        response = self._hook(
            "security/public-key-certificates", post=False)
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
            elif status == 200:
                return
            else:
                raise ValueError(
                    f"Session activation failed: {status} - {description}")

        raise TimeoutError("Session activation timed out.")

    def session_terminate(self) -> None:
        # TODO: Do not use
        # TODO: not working?
        url = f"auth/sessions/{self._referencenumber}"
        # url = "auth/sessions/current"
        self._hook(url, post=False, dele=True, withbearer=True)

    def start_session(self):
        encrypted_symmetric_key = encrypt_symmetric_key(
            symmetricy_key=self._symmetric_key,
            public_certificate=self._public_certificate
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
                              body=request_data, withbearer=True, post = False)
        print(response)
