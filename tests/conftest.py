import pytest
from pydent import AqSession
from pydent.browser import Browser


@pytest.fixture(scope='function')
def session():
    return AqSession("vrana", "Mountain5", "http://52.27.43.242/")


@pytest.fixture(scope="function")
def browser(session):
    return Browser(session)
