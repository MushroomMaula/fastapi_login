## Cookies
By default ``LoginManager`` expects the token to be in the ``Authorization``
header. However cookie support can be enabled.
````python hl_lines="5"
{!../docs_src/advanced_usage/adv_usage_001.py!}
````

For convince as ``set_cookie`` method is provided, which sets the cookie, using
``LoginManager.cookie_name`` and the recommended ``HTTPOnly`` flag.

````python hl_lines="7"
{!../docs_src/advanced_usage/adv_usage_003.py!}
````

### Configuration
By default, ``LoginManager`` looks for a cookie with the name ``access-token``,
this can be changed using the ``cookie_name`` property.
````python
manager.cookie_name = 'custom-cookie-name'
````
If you only want to support authorization using cookies, ``use_header`` can be set
to false on initialization.
````python hl_lines="6"
{!../docs_src/advanced_usage/adv_usage_002.py!}
````

## Exception handling
Sometimes it is needed to run some code if a user is not authenticated,
this can achieved, by setting a custom ``Exception`` on the ``LoginManager`` instance.

````python hl_lines="9"
{!../docs_src/advanced_usage/adv_usage_004.py!}
````

Now whenever there is no, or an invalid token present in the request, your exception
will be raised, and the exception handler will be executed.

More to writing exception handlers can be found in the official [documentation](https://fastapi.tiangolo.com/tutorial/handling-errors/?h=+exce#install-custom-exception-handlers)
of FastAPI

## Token expiry
By default token's expire after 15 minutes. This can be changed using the ``expires``
argument in the ``create_access_token`` method.

````python
{!../docs_src/advanced_usage/adv_usage_005.py!}
````