@manager.user_loader(db_session=...)
def query_user(user_id: str, db_session):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :param db_session: The currently active connection to the database
    :return: None or the user object
    """
    return db_session.get(user_id)
