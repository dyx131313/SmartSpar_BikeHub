import inspect
import os

import pytest
from sqlalchemy import text


os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-testing-only")
os.environ.setdefault("MYSQL_DATABASE", "bikehub_test_test")


@pytest.fixture(scope="session", autouse=True)
def reset_test_database():
    """Start each pytest run from a clean MySQL test schema."""
    from app import create_app, db

    app = create_app("testing")
    with app.app_context():
        with db.engine.begin() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            db.metadata.drop_all(bind=connection)
            db.metadata.create_all(bind=connection)
            connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """Allow legacy script-style tests to return True/False under pytest 8."""
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        return None

    testargs = {
        arg: pyfuncitem.funcargs[arg]
        for arg in pyfuncitem._fixtureinfo.argnames
    }
    result = testfunction(**testargs)
    if result is False:
        pytest.fail("Legacy script-style test returned False")
    return True
