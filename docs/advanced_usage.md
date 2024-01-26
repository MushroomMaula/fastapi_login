## Cookies

By default ``LoginManager`` expects the token to be in the ``Authorization``
header. However cookie support can be enabled.

```python hl_lines="3"
{!../docs_src/advanced_usage/adv_usage_001.py!}
```

For convenince a ``set_cookie`` method is provided, which sets the cookie, using
``LoginManager.cookie_name`` and the recommended ``HTTPOnly`` flag.

```python hl_lines="5"
{!../docs_src/advanced_usage/adv_usage_003.py!}
```

### Configuration

By default, ``LoginManager`` looks for a cookie with the name ``access-token``,
this can be changed using the ``cookie_name`` argument, when creating the instance.

```python
manager = LoginManager(
    ...,
    cookie_name='custom-cookie-name'
)
```

If you only want to support authorization using cookies, ``use_header`` can be set
to false on initialization.

```python hl_lines="3"
{!../docs_src/advanced_usage/adv_usage_002.py!}
```

## Exception handling

Sometimes it is needed to run some code if a user is not authenticated,
this can achieved, by setting a custom ``Exception`` on the ``LoginManager`` instance.

```python hl_lines="14"
{!../docs_src/advanced_usage/adv_usage_004.py!}
```

Now whenever there is no, or an invalid token present in the request, your exception
will be raised, and the exception handler will be executed.

More to writing exception handlers can be found in the official [documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/?h=+exce#install-custom-exception-handlers)
of FastAPI

## Token expiry

By default token's expire after 15 minutes. This can be changed using the ``expires``
argument in the ``create_access_token`` method.

```python
{!../docs_src/advanced_usage/adv_usage_005.py!}
```

If you want to change the expiry for every token issued the default expiry
can be set on initialization

```python
manager = LoginManager(
    ...,
    default_expiry=timedelta(hours=12)
)
```

## Middleware

Optionally a ``LoginManager`` instance can also be added as a middleware.
It's important to note that ```request.state.user``` is set to ``None`` if
no (valid) token is present in the request.

```python hl_lines="3"
{!../docs_src/advanced_usage/adv_usage_006.py!}
```

Using the middleware it's easy to write your own dependencies, that have access
to your user object.

```python hl_lines="6"
{!../docs_src/advanced_usage/adv_usage_007.py!}
```

## OAuth2 scopes

In addition to normal token authentication, OAuth2 scopes can be used to restrict
access to certain routes.

```python hl_lines="2"
{!../docs_src/advanced_usage/adv_usage_008.py!}
```

Notice how instead of the normally used ``fastapi.Depends`` ``fastapi.Security`` is used.
In order to give your token the required scopes [``LoginManager.create_access_token``](reference.md#fastapi_login.fastapi_login.LoginManager.create_access_token)
has a ``scopes`` parameter.
In order for the scopes to show up in the OpenAPI docs, your scopes need to be passed
as an argument when instantiating LoginManager.

## Predefining additional ``user_loader`` arguments

The ``LoginManager.user_loader`` can also take arguments which will be passed on the
callback

```python hl_lines="1"
{!../docs_src/advanced_usage/adv_usage_009.py!}
```

!!! bug "Callable as extra argument"
    Before version 1.7.0 empty parentheses were not needed after the decorator.
    To provide backwards compatibility it's still possible to omit them as of v1.7.1.
    Because of this it's however not possible to pass a callable object as the
    first extra argument.

    This will not work:
    ```py
    def some_callable_object(...):
        ...

    @manager.user_loader(some_callable_object)
    def load_user(email, some_callable):
        ...
    ```
    If you need this functionality you need to use keyword arguments:
    ```py
    @manager.user_loader(some_callable=some_callable_object)
    def load_user(email, some_callable)
    ```

## Asymmetric algorithms

Thanks to [filwaline](https://github.com/filwaline) in addition to symmetric keys, RSA can also
be used to sign the tokens.
!!!note "Required dependencies"
    The cryptography packages is required for this.
    Run the following command to install all the required dependencies.
    ```
    pip install fastapi-login[asymmetric]
    ```
??? help "Supported algorithms"
    Currently ```RS256``` is the only asymmetric algorithm supported by the package.
    If you need another algorithm, please open an
    [issue](https://github.com/MushroomMaula/fastapi_login/issues/new) and I will
    consider adding it.
To use the asymmetric algorithm choose ``algorithm="RS256"`` when initiating `LoginManager`.

```python hl_lines="3"
LoginManager(
    secret="...", token_url="...",
    algorithm="RS256"
)
```

If your private key is not password protected the usage of the package stays exactly the same.
!!!hint
    You don't need to pass your public key explicitly, as it can be derived from the private key.

However, if you used a password during the key generation the syntax changes slightly.

```python hl_lines="2 4"
{!../docs_src/advanced_usage/adv_usage_010.py!}
```

Note how instead of just using the key, we now have to pass a dictionary with the
`private_key` and the `password` fields set.
