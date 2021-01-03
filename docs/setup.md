# Set up

First we need to set up our FastAPI app:
````python
from fastapi import FastAPI
app = FastAPI()
````

Now we declare a secret key. We define our key as a global value for simplicity, 
normally one would store the secret key in some sort of environment variable.

````Python hl_lines="4"
{!../docs_src/setup/setup_001.py!}
````

!!! warning
    To obtain a suitable key run the following command in your shell.
    ````
    python -c "import os; print(os.urandom(24).hex())"
    ````

Now we start setting up ``fastapi-login`` by importing `LoginManager`.
````Python hl_lines="2"
{!../docs_src/setup/setup_002.py!}
````

The ``LoginManager`` expects two arguments on initialization, a secret used to
encrypt and decrypt the tokens, and the url where one can obtain the token in 
your application. The url is needed in order to display correctly inside the api docs.
````python hl_lines="7"
{!../docs_src/setup/setup_003.py!}
````

Thats all you need to setup the ``LoginManager`` object.

!!! note
    The provided url should be the same your users use to obtain a token.

Now that we have created a new instance of ``LoginManager``, we need to setup
our database.

First we need a way to query a user from the db. For this example we will use
a dictionary in order to model a database.
````python
{!../docs_src/setup/setup_004.py!}
````

Now that we have our "database" setup, and a way to retrieve a user 
we need to pass this function to our manager object, this way ``LoginManager``
automatically can return the user object.
````python hl_lines="1"
{!../docs_src/setup/setup_005.py!}
````

!!! note 
    ``manager`` in this context is an instance of ``LoginManager`` 

To see how to use ``fastapi-login`` as a dependency continue with [usage](usage.md)