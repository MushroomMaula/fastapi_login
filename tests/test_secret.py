from fastapi_login.secrets import Secret, SymmetricSecret, AsymmetricSecret
from pydantic import parse_obj_as, ValidationError
import pytest
import secrets


def generate_rsa_key(key_size=2048):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=key_size
    )
    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return private_key


@pytest.mark.parametrize(
    ("secret_type", "alg", "secret"),
    [
        (SymmetricSecret, "HS256", secrets.token_hex(16)),
        (AsymmetricSecret, "RS256", generate_rsa_key(512).decode()),
        (AsymmetricSecret, "RS256", {"private_key": generate_rsa_key(512)}),
        #
        # Treat rsa-private-key as secret
        (SymmetricSecret, "HS256", generate_rsa_key(512)),
    ],
)
def test_secret_parsing_happypath(secret_type, alg, secret):
    s = parse_obj_as(Secret, {"algorithms": alg, "secret": secret})
    assert isinstance(s, secret_type)


def test_secret_parsing_case_mismatched_1():
    with pytest.raises(ValidationError, match="Secret is not an asymmetric key."):
        parse_obj_as(Secret, {"algorithms": "RS256", "secret": secrets.token_hex(16)})


def test_secret_parsing_case_mismatched_2():
    with pytest.raises(ValidationError, match="Secret is not an asymmetric key."):
        parse_obj_as(
            Secret,
            {"algorithms": "RS256", "secret": {"private_key": secrets.token_hex(16)}},
        )
