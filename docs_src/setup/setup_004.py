DB = {"users": {"johndoe@mail.com": {"name": "John Doe", "password": "hunter2"}}}


def query_user(user_id: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    return DB["users"].get(user_id)
