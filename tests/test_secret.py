import secrets

import pytest
from pydantic import ValidationError

from fastapi_login.secrets import AsymmetricSecret, SymmetricSecret, to_secret

from .conftest import generate_rsa_key, require_cryptography

happypath_parametrize_argvalues = [
    pytest.param(
        SymmetricSecret,
        "HS256",
        secrets.token_hex(16).encode(),
    ),
    pytest.param(
        AsymmetricSecret,
        "RS256",
        generate_rsa_key(512),
        marks=require_cryptography,
    ),
    pytest.param(
        AsymmetricSecret,
        "RS256",
        {"private_key": generate_rsa_key(512)},
        marks=require_cryptography,
    ),
    pytest.param(
        AsymmetricSecret,
        "RS256",
        {
            "private_key": generate_rsa_key(512, b"qwer1234"),
            "password": b"qwer1234",
        },
        marks=require_cryptography,
    ),
    #
    # Treat rsa-private-key as secret
    pytest.param(
        SymmetricSecret, "HS256", generate_rsa_key(512), marks=require_cryptography
    ),
]


@pytest.mark.parametrize(
    ("secret_type", "alg", "secret"), happypath_parametrize_argvalues
)
def test_secret_parsing_happypath(secret_type, alg, secret):
    s = to_secret({"algorithms": alg, "secret": secret})
    assert isinstance(s, secret_type)


invalid_parametrize_argvalues = [
    pytest.param("HS256", None),
    pytest.param("HS256", {"private_key": secrets.token_hex(16)}),
    pytest.param(
        "HS256", {"private_key": generate_rsa_key(512)}, marks=require_cryptography
    ),
    pytest.param("RS256", None),
    pytest.param("RS256", secrets.token_hex(16).encode()),
    pytest.param("RS256", {"private_key": secrets.token_hex(16)}),
    pytest.param(
        "RS256",
        {
            "private_key": generate_rsa_key(512, b"password"),
            "password": b"wrong-password",
        },
        marks=require_cryptography,
    ),
]


@pytest.mark.parametrize(("alg", "secret"), invalid_parametrize_argvalues)
def test_secret_parsing_case_invalid_input(alg, secret):
    with pytest.raises(ValidationError):
        to_secret({"algorithms": alg, "secret": secret})
