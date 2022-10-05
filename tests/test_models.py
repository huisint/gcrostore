import datetime
import typing as t
from unittest import mock

import pytest
from crostore import config as crostore_config
from selenium import webdriver

from gcrostore import models
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
                return webdriver.FirefoxOptions().to_capabilities()  # type: ignore[no-untyped-call]
            case "ie":
                return webdriver.IeOptions().to_capabilities()  # type: ignore[no-untyped-call]
            case _:
                raise ValueError(f"Invalid request param: {request.param}")

    @pytest.fixture()
    def selenium(url: str, desired_capabilities: dict[str, t.Any]) -> models.Selenium:
        return models.Selenium(url=url, desired_capabilities=desired_capabilities)

    @mock.patch("selenium.webdriver.Remote", spec_set=webdriver.Remote)
    def test_driver(remote_mock: mock.Mock, selenium: models.Selenium) -> None:
        with selenium.driver() as driver:
            assert driver == remote_mock.return_value
            remote_mock.return_value.quit.assert_not_called()
        remote_mock.return_value.quit.assert_called_once_with()
        remote_mock.assert_called_once_with(
            selenium.url, desired_capabilities=selenium.desired_capabilities
        )
        remote_mock.return_value.implicitly_wait.assert_called_once_with(
            crostore_config.SELENIUM_WAIT
        )


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

    @mock.patch("google.oauth2.credentials.Credentials.refresh")
    def test_creds_that_requires_refresh(
        refresh_mock: mock.Mock, creds: dict[str, t.Any], sheet_id: str
    ) -> None:
        creds["expiry"] = _format_expiry(
            datetime.datetime.now() - datetime.timedelta(days=1)
        )
        models.Google(creds=creds, sheet_id=sheet_id)
        refresh_mock.assert_called_once()
