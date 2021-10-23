# About
This project implements a simple blogging platform with user accounts, to showcase how to work with `fastapi-login`.

# Getting started
First you have to download this project, there are various methods how to download only this folder.
 - https://download-directory.github.io/ Downloads the folder as a zip file.
 - Clone the complete project and enter the examples folder by hand.

Next we have to create a virtual environement to install the dependencies
`python -m venv venv`
After activating the newly created environement we can install the project's dependencies
`pip install -r requirements.txt`

Before we can run the webapp we need to create a suitable secret key and a admin user:

`python main.py create-secret`

`python main.py create-admin <username> <password>`

Now we can start running the application

`python main.py start`

This will start the application on [127.0.0.1:8000](127.0.0.1:8000).

Visist [127.0.0.1:8000/docs](127.0.0.1:8000/docs) to try out the API.

# Technical information
We will use `fastapi-login` for authentication and `sqlalchemy` together with `sqlite` as our database.
`python-dotenv` is used in combination with pydantics `BaseConfig` for config management.
All code concerning `fastapi-login` is contained inside the `app/auth` folder.