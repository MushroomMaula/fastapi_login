manager = LoginManager(
    secret={"private_key": "your_rsa_key", "password": "your_password_for_the_key"},
    token_url="...",
    algorithm="RS256",
)
