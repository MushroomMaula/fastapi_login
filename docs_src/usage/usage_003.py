@app.get('/protected')
def protected_route(user=Depends(manager)):
    return {'user': user}