from fastapi.requests import Request

manager.attach_middleware(app)

@app.route("/showcase")
def showcase(request: Request):
    # None if unauthorized
    user = request.state.user
