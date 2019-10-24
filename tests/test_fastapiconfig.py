import pytest
from starlette.datastructures import Secret


def test_config_init(app, config):

    assert app.config == config


def test_config_set_get(app, config):
    value = 'sqlite:///path/to/db'
    config.DATABASE_URI = value
    config['test'] = value

    assert config.DATABASE_URI == value
    assert config['test'] == value


def test_config_del(config):
    value = 'super-secret'
    config.secret = value
    assert config.secret == value
    del config['secret']
    with pytest.raises(AttributeError):
        _ = config.secret


def test_set_secret(config):
    secret = "super-secret"
    config.set_secret(secret)

    assert isinstance(config.secret, Secret)
    assert str(config.secret) == secret
