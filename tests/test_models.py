import datetime
import typing as t

import pydantic
import pytest
import pytest_mock
from crostore import config as crostore_config
from selenium import webdriver

from gcrostore import config, models
from tests import FixtureRequest


def describe_selenium() -> None:
    @pytest.fixture(
        params=["http://example.com:4444/wd/hub"],
    )
    def url(request: FixtureRequest[str]) -> str:
        return request.param

    @pytest.fixture(params=["chrome", "firefox", "ie"])
    def desired_capabilities(request: FixtureRequest[str]) -> dict[str, t.Any]:
        match request.param:
            case "chrome":
                return webdriver.ChromeOptions().to_capabilities()
            case "firefox":
                return webdriver.FirefoxOptions().to_capabilities()
            case "ie":
                return webdriver.IeOptions().to_capabilities()
            case _:
                raise ValueError(f"Invalid request param: {request.param}")

    @pytest.fixture()
    def selenium(
        url: pydantic.HttpUrl, desired_capabilities: dict[str, t.Any]
    ) -> models.Selenium:
        return models.Selenium(url=url, desired_capabilities=desired_capabilities)

    def test_driver(
        selenium: models.Selenium, mocker: pytest_mock.MockerFixture
    ) -> None:
        mocker.patch(
            "selenium.webdriver.remote.remote_connection.RemoteConnection.execute",
            side_effect=[
                {
                    "status": 0,
                    "value": {
                        "sessionId": None,
                        "capabilities": None,
                    },
                },  # response for Command.NEW_SESSION
                {
                    "status": 0,
                    "value": {},
                },  # response for Command.QUIT
            ],
        )
        implicitly_wait_mock = mocker.patch("selenium.webdriver.Remote.implicitly_wait")
        with selenium.driver() as driver:
            assert isinstance(driver, webdriver.Remote)
        implicitly_wait_mock.assert_called_once_with(crostore_config.SELENIUM_WAIT)


def _format_expiry(dt: datetime.datetime) -> str:
    return dt.isoformat(timespec="seconds") + "Z"


def describe_google() -> None:
    @pytest.fixture()
    def creds() -> dict[str, t.Any]:
        fake_token = "fake_token"
        fake_refresh_token = "fake_refresh_token"
        fake_client_id = "fake_client_id"
        fake_client_secret = "fake_client_secret"
        expiry = datetime.datetime.now() + datetime.timedelta(days=1)
        creds = {
            "token": fake_token,
            "refresh_token": fake_refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": fake_client_id,
            "client_secret": fake_client_secret,
            "scopes": config.scopes,
            "expiry": _format_expiry(expiry),
        }
        return creds

    @pytest.fixture()
    def sheet_id() -> str:
        return "sheet_id"

    def test_creds_valid(creds: dict[str, t.Any], sheet_id: str) -> None:
        google = models.Google(creds=creds, sheet_id=sheet_id)
        assert google.creds == creds

    def test_creds_that_requires_refresh(
        creds: dict[str, t.Any],
        sheet_id: str,
        mocker: pytest_mock.MockerFixture,
    ) -> None:
        refresh_mock = mocker.patch("google.oauth2.credentials.Credentials.refresh")
        creds["expiry"] = _format_expiry(
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
        models.Google(creds=creds, sheet_id=sheet_id)
        refresh_mock.assert_called_once()
