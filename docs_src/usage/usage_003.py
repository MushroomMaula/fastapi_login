@app.get('/proteced')
def protected_route(user=Depends(manager)):
    return {'user': user}