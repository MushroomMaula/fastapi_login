@app.get("/protected")
def protected_route(user=Depends(manager.optional)):
    if user is None:
        # Do something ...
        pass
    return {"user": user}
