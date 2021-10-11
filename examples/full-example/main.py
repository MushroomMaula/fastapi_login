import os
import argparse
from dotenv import dotenv_values
from app.db import create_tables, get_session
from app.db.actions import create_user


def create_secret(_args):
    """
    Creates a secret and stores it in a .env file in the current working directory
    Use `python main.py create-secret --help` for more options
    Args:
        _args: The parsed command line arguments
    """

    config = dotenv_values('.env')

    # No .env file exists or no secret key has been set
    if config is None or config.get('SECRET') is None:
        with open('.env', 'a') as f:
            f.write(f'SECRET={os.urandom(24).hex()}')

        print(f"Secret stored at {os.path.abspath('.env')}")
    else:
        print("A secret already exists. Use --overwrite to create a new secret.")
        if _args.overwrite:
            with open('.env', 'w') as f:
                for key, value in config.items():
                    if key == 'SECRET':
                        value = os.urandom(24).hex()
                    f.write(f"{key}={value}")


def create_admin(_args):
    session = next(get_session())
    create_user(args.username, args.password, session, is_admin=True)
    print("Admin created.")


def run(_args):
    import uvicorn
    from app.app import app
    uvicorn.run(app)


parser = argparse.ArgumentParser(description='CLI to setup our blogging API.')
subparsers = parser.add_subparsers()

secret_parser = subparsers.add_parser('create-secret', help="Writes a suitable secret key to a .env file in the current working directory.")
secret_parser.add_argument('--overwrite', action='store_true', help="Overwrite the present secret value.")
secret_parser.set_defaults(func=create_secret)

db_parser = subparsers.add_parser('create-db', help="Creates the tables and the databses for the project")
db_parser.set_defaults(func=create_tables)

admin_parser = subparsers.add_parser('create-admin', help="Creates a admin user with the given password and username.")
admin_parser.add_argument('username', help="Username of the admin.")
admin_parser.add_argument('password', help="Password of the amdin.")
admin_parser.set_defaults(func=create_admin)

start_parser = subparsers.add_parser('start', help="Starts the API")
start_parser.set_defaults(func=run)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)  # Call the function with the given arguments, it is assumed that every parser sets the corresponding function