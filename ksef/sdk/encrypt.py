import base64
import datetime
import calendar
import os
import hashlib

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def _encode(s: str) -> bytes:
    return s.encode('utf-8')


def to_base64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def _public_key(public_certificate: str):
    crt = f'-----BEGIN CERTIFICATE-----\n{public_certificate}\n-----END CERTIFICATE-----'

    certificate = x509.load_pem_x509_certificate(_encode(crt))
    public_key = certificate.public_key()
    return public_key


def _encrypt_public_key(public_certificate: str, to_encrypt: bytes) -> bytes:
    public_key = _public_key(public_certificate)
    encrypted = public_key.encrypt(
        to_encrypt,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


def encrypt_token(kseftoken: str, timestamp: str, public_certificate: str) -> str:
    t = datetime.datetime.fromisoformat(timestamp)
    t = int((calendar.timegm(t.timetuple()) * 1000) + (t.microsecond / 1000))
    token_bytes = _encode(f"{kseftoken}|{t}")
    encrypted = _encrypt_public_key(
        public_certificate=public_certificate, to_encrypt=token_bytes)
    return to_base64(encrypted)


def get_key_and_iv() -> tuple[bytes, bytes]:
    symmetric_key = os.urandom(32)
    iv = os.urandom(16)
    return symmetric_key, iv


def encrypt_symmetric_key(symmetricy_key: bytes, public_certificate: str) -> bytes:
    encrypted_symmetric_key = _encrypt_public_key(
        public_certificate=public_certificate, to_encrypt=symmetricy_key)
    return encrypted_symmetric_key


def _pad(data: bytes) -> bytes:
    padding_length = 16 - len(data) % 16
    padding = bytes([padding_length] * padding_length)
    return data + padding


def encrypt_invoice(symmetric_key: bytes, iv: bytes, invoice: str) -> tuple[int, bytes]:
    invoice_bytes = _encode(invoice)
    cipher = Cipher(
        algorithms.AES(symmetric_key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    padded_invoice = _pad(invoice_bytes)
    encrypted_invoice = encryptor.update(padded_invoice) + encryptor.finalize()
    return len(invoice_bytes), encrypted_invoice


def calculate_hash(data: bytes | str) -> str:
    if isinstance(data, str):
        data = _encode(data)
    return base64.b64encode(hashlib.sha256(data).digest()).decode()
