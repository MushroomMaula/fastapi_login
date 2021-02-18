from fastapi.requests import Request

manager.useRequest(app)

@app.route('/showcase')
def showcase(request: Request):
    # None if unauthorized
    user = request.state.user