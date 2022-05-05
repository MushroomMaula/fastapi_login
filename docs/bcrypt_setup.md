## You want to use bcrypt & fastapi-login Manager for authentication?
<br>
You've came to the right place !
<br><br>
Let's assume you got `FastAPI` , `fastapi-login` , `bcrypt` , `python-multipart` all installed using `pip`

## main.py

Let's break it down: This File is my Webserver, and I've got *2 POST ENDPOINTS* 

* `/api/token` which authenticates a profile.
* `/restricted` which can only be accessed by authenticated profile.

I'll break `main.py` up into 2 chunks, so I can explain each endpoint better. <br>( Part I )

```python
from fastapi import FastAPI, HTTPException
from path.to.file import auth
import uvicorn

app = FastAPI()

@app.post('/api/token')
async def login(req: Request, data: OAuth2PasswordRequestForm = Depends()): 
    #Depends is basically asserting the incoming request (If allowed to access or not)
    #Here it doesn't make much sense, but below you'll see a use case for it

    # These are from my frontend (I sent a JSON Post Body in)
    username = data.user
    password = data.passwd 

    #Search if the username exists as a row in my database (Or JSON if it's NoSQL) 
    user = auth.load_user(username) 

    #Raising some basic exceptions for cases we'll run into
    #Users typing in wrong user/pass combos, users trying to login as none existent profiles

    if user is None:
        return HTTPException(status_code=404, detail="Username wasn't found.")

    if not auth.verify_password(password, user[2]):
        return HTTPException(status_code=403, detail="Wrong password for this profile.")

    #Here is where We use fastapi_login's .create_access_token() function to generate a JWT with PK as username (in this case)

    access_token = auth.manager.create_access_token(
        data={
            "sub": username, #IMPORTANT: The Primary key here always needs to be titled "sub" (Further Explanation below)
        }
    )

    #Now it returns my JWT (access token) & the token type, in this case: "bearer" (bearer of token, bearer of profile)

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }
```

When the `/api/token` endpoint gets called, it either throws an error with a detail (to be broadcasted on the frontend) or with a JSON object containing the user's access token, along with the token's type.

The idea is you store is as a cookie on the frontend.
![Cookie](/docs_src/b_setup/cookie.png)
The cookies should look like this in your browser.

here is the access_token, this is also known as a JWT or (json web token). 
<br><br>
`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJKYXNvbjEiLCJleHAiOjE2NTE3MjQ0NzR9.19YBAn_Ewf6IiRg_vbMztJz5XW_19Qw5x93Q_CeOer8`
<br><br>
Fastapi-login's <br>```manager.create_access_token``` or in our case, we hold the manager function in the auth module `auth.manager.create_access_token` . creates a JWT using a secret key. 

Let's say our secret-key is: `"your-secret-key"`

![JWT invalid](/docs_src/b_setup/jwt_invalid.png)

Here you can see the signature is invalid since it isn't our secret_key, FastAPI knows this key `(View auth.py module where it's set)` however our users don't. This way people can't just change the sub of the JWT and login as a different user.

Now that we've got our Login endpoint that returns a JWT signed with our secret-key, let's move onto looking at endpoints that require an **authenticated user** to **access**.

## main.py ( Part II )

```python
@app.post('/api/token')
async def login(req: Request, data: OAuth2PasswordRequestForm = Depends()): 
    #logins in user..

#Main.py P.2 :

@app.get('/api/me')
async def secure(req: Request, user=Depends(auth.manager)):
    #Depends isn't empty this time, this GET endpoint requires the auth.manager to load the user before receiving a successful response.

    if user:
        return {"valid": "welcome back!"}
```

Depends will automatically handle an incorrect credentials (An invalid token & token_type) with a `401 Unauthorized` Status Code along with some basic detail like `"Invalid Credentials ! You either aren't logged in, or your cookies are rotten!`.

Or else, you'll get a `200 OK` along with the JSON body.

We'll look further into how the Depends(auth.manager) works below:

## auth.py

```python
import bcrypt
import hashlib  # hashlib is actually built-into python
import base64
import json

from fastapi_login import LoginManager


SECRET = 'your-secret-key' #This is the signature to our JWT access-tokens, store this in a PATH variable or .env file.

manager = LoginManager(SECRET, token_url="/api/token", use_cookie=True) #This is our auth.manager you see being called by the Endpoint's Depends()


#Here we use bcrypt to hash a plain-text password:
#This method is used for the creation of user, so you'd hasg your plaintext pass hash_password('string') and you Insert that. 
# (User creation isn't covered in this guide)

def hash_password(password: str) -> str:

    if isinstance(password, str):
        password.encode()

    # Taken from the bcrypt docs (Work around for 72 char limit)

    return bcrypt.hashpw(
        base64.b64encode(hashlib.sha256(password.encode()).digest()),
        bcrypt.gensalt(12)
    ).decode()

    #This work-arround was found on the bcrypt pip docs.

def verify_password(password: str, hashed_password: str):

    if isinstance(password, str):
        password = password.encode()

    #Here i'm turning password into a base64 encoded SHA256 str from our input password field.

    check_hash = base64.b64encode(
            hashlib.sha256(
                password
            ).digest()
        )

    #bcrypt makes it easy to compare the passwords via checkpw() function. (Make sure you encode() the hashed password you're pulling from your database)

    return bcrypt.checkpw(
       check_hash,
        hashed_password.encode()
    )

@manager.user_loader() #hooks function below
def find_user(user_query: str) -> json:

    #Just a placeholder for your database fetch:
    user = Database.search(user_query)

    if user is None:
        return 
    
    return user
```
<h3> Hash password:</h3><br>

When you're saving a hashed-pw in your database, it should look something like this:<br>
`$2b$12$dJyrKT5HWOzOVaPvsRruVOsMD57j5KpgJ2HInFi9h6ONqjBlhGKa`
<br><br>

<h3> Manager's user loader & relation to find_user:</h3><br>

Basically, in `main.py` , when endpoints are using the `Depends(auth.manager)` , the manager looks for the function hooked to `@manager.user_loader()` In this case we've called it `find_user`. Manager will now use this function along with some internal processing of the JWT (using the `SECRET`) to either validate or invalidate the Depends callback.
<br><br>
**BE CAREFUL;** about how you structure the `find_user` function.<br><br>**FastAPI-login** wants this to take in **1** parameter *(A distinguishable feature from the profile, in this case I'm assuming the username as they are all unique, therefore my unique identifier)* <br><br> And return either the user's object (JSON, Class, ...) or **None**.<br><br>














