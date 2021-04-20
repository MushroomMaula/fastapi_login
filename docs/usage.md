Now that you have [setup](setup.md) everything, lets get started using 
``fastapi-login``.

## Login route
First we need to create a login route for our users.
````python
{!../docs_src/usage/usage_001.py!}
````

!!! note
    We use the same url(``"/login"``) we have used as the ``tokenUrl`` argument,
    when initiating our ``LoginManager`` instance

## Returning token
Now that we have created a login route, we want to return a token, which can than
be used to access protected routes.
````python hl_lines="13 14 15 16"
{!../docs_src/usage/usage_002.py!}
````

!!! attention    
    ``LoginManager`` expects the parameter used in your ``LoginManager.user_loader``
    function to be in the ``sub`` field of the token. This conforms the official
    [specification](https://tools.ietf.org/html/rfc7519#page-9) of json web tokens.

## Usage as a dependency
After the user has way to obtain an access_token, the ``LoginManager`` instance
can be used as a dependency.
````python hl_lines="2"
{!../docs_src/usage/usage_003.py!}
````

!!! note 
    ``user`` in this case will be whatever ``LoginManager.user_loader`` returns.
    In case user is ``None`` the `LoginManager.not_authenticated_exception`
    will be thrown, this results into a 401 http status code by default.
    If ```not_authenticated_exception``` has been set by the user it will be
    raised instead.
