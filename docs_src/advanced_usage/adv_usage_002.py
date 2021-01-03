from fastapi_login import LoginManager

manager = LoginManager(
    'secret', '/login',
    use_cookie=True,
    use_header=False
)