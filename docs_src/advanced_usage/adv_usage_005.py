# expires after 12 hours
long_token = manager.create_access_token(data=data, expires=timedelta(hours=12))
