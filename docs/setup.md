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

To see how to use ``fastapi-login`` as a dependency continue with [usage](usage.md)
