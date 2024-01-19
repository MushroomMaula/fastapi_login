# About

This example shows how to integrate the sqlalchemy orm with ``fastapi-login``. However the basic idea should be
applicable to other ORM frameworks as well.

How to handle the database session can be found in ``db_actions.py`` and ``db.py``

## Run

Install the dependencies

```
pip install -r requirements.txt
```

Create a new .env file containing a secure secret

```
python create_dotenv.py
```

Run the app

```
python app.py
```

Go to `127.0.0.1/docs` in your browser.
