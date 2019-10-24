import typing

from starlette.applications import Starlette
from starlette.datastructures import Secret


class FastAPIConfig(object):

    def __init__(self, app=None, config=None, *args, **kwargs):

        if app is None:
            base = {}
        else:
            base = {'APP': app}

        if config is None:
            _config = base
        else:
            _config = base.update(config)

        super(FastAPIConfig, self).__setattr__('_config', _config)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Starlette):
        app.config = self

    def set_secret(self, secret: str):
        self._config['secret'] = Secret(secret)

    def get(self, key: typing.Any) -> typing.Any:
        try:
            item = self._config[key]
        except KeyError:
            return
        return item

    def __setattr__(self, key: typing.Any, value: typing.Any) -> None:
        self._config[key] = value

    def __getattr__(self, key: typing.Any) -> typing.Any:
        try:
            return self._config[key]
        except KeyError:
            message = "'{}' object has no attribute '{}'"
            raise AttributeError(message.format(self.__class__.__name__, key))

    def __delitem__(self, key: typing.Any):
        del self._config[key]

    def __getitem__(self, key: typing.Any):
        return getattr(self, key)

    def __setitem__(self, key: typing.Any, value: typing.Any):
        setattr(self, key, value)

