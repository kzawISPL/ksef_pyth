from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import datetime
import calendar


def encrypt_token(kseftoken: str, timestamp: str, public_certificate: str) -> str:
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
        padding.OAEP(
            mgf=padding.MGF1(algorithm=padding.hashes.SHA256()),
            algorithm=padding.hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode("utf-8")
