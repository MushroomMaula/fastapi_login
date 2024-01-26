@app.post("/login")
def login(response: Response):
    ...
    token = manager.create_access_token(data=dict(sub=user.email))
    manager.set_cookie(response, token)
    return response
