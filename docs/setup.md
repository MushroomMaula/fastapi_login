First we need to set up our FastAPI app:

```python
from fastapi import FastAPI
app = FastAPI()
```

## Secret

Now we declare a secret key. We define our key as a global value for simplicity,
normally one would store the secret key in some sort of environment variable.

```Python hl_lines="5"
{!../docs_src/setup/setup_001.py!}
```

!!! warning
    To obtain a suitable key run the following command in your shell.
    ```
    python -c "import os; print(os.urandom(24).hex())"
    ```
!!! warning
    Most of the time it's better not to store the secret key in a file like this,
    but rather in an environment variable, in order to avoid committing it to
    source control.

## LoginManager

Now we start setting up ``fastapi-login`` by importing `LoginManager`.

```Python hl_lines="3"
{!../docs_src/setup/setup_002.py!}
```

The ``LoginManager`` expects two arguments on initialization, a secret used to
encrypt and decrypt the tokens, and the url where one can obtain the token in
your application. The url is needed in order to display correctly inside the api docs.

```python hl_lines="8"
{!../docs_src/setup/setup_003.py!}
```

Thats all you need to setup the ``LoginManager`` object.

!!! note
    The provided url should be the same your users call to obtain a token.

## Database

Now that we have created a new instance of ``LoginManager``, we need to setup
our database.

First we need a way to query a user from the db. For this example we will use
a dictionary in order to model a database.

```python
{!../docs_src/setup/setup_004.py!}
```

Now that we have our "database" setup, and a way to retrieve a user
we need to pass this function to our manager object, this way ``LoginManager``
automatically can return the user object.
It's as simple as it gets, you just have to add this decorator to the query function.

```python hl_lines="1"
{!../docs_src/setup/setup_005.py!}
```

!!! note
    ``manager`` in this context is an instance of ``LoginManager``

!!! bug "Callable as extra argument"
    Before version 1.7.0 the empty parentheses were not needed after the decorator.
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

To see how to use ``fastapi-login`` as a dependency continue with [usage](usage.md).
