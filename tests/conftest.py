import pytest
from pydent import AqSession
from pydent.browser import Browser
import os
import json


@pytest.fixture(scope="session")
def config():
    """
    Returns the config dictionary for live tests.
    """
    dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(dir, "secrets", "config.json.secret")
    with open(config_path, 'rU') as f:
        config = json.load(f)
    return config


@pytest.fixture(scope="session")
def session(config):
    """
    Returns a live aquarium connection.
    """
    return AqSession(**config)


@pytest.fixture(scope="function")
def browser(session):
    return Browser(session)
