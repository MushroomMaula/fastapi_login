@app.get('/protected')
def protected_route(user=Depends(manager.optional)):
    if user is None:
        # Do something ...
    return {'user': user}