from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64
import datetime
import calendar
import os


def _public_key(public_certificate: str):
    crt = f'-----BEGIN CERTIFICATE-----\n{public_certificate}\n-----END CERTIFICATE-----'

    certificate = x509.load_pem_x509_certificate(
        crt.encode("utf-8")
    )
    public_key = certificate.public_key()
    return public_key


def encrypt_token(kseftoken: str, timestamp: str, public_certificate: str) -> str:
    public_key = _public_key(public_certificate)

    #t = datetime.datetime.fromisoformat(timestamp)
    #t = int((calendar.timegm(t.timetuple()) * 1000) + (t.microsecond / 1000))
    token_bytes = f"{kseftoken}|{timestamp}".encode('utf-8')

    encrypted = public_key.encrypt(
        token_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    #return base64.b64encode(encrypted).decode("utf-8")
    return to_base64(encrypted)


def to_base64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def get_key_and_iv() -> tuple[bytes, bytes]:
    symmetric_key = os.urandom(32)
    iv = os.urandom(16)
    return symmetric_key, iv


def encrypt_symmetric_key(symmetricy_key: bytes, public_certificate: str) -> bytes:
    public_key = _public_key(public_certificate)
    encrypted_symmetric_key = public_key.encrypt(
        symmetricy_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return encrypted_symmetric_key
