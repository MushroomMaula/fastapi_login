@app.get("/scoped/route")
def scoped_route(user=Security(manager, scopes=["required", "scopes", "here"])):
    ...
