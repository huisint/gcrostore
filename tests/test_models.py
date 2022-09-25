import typing as t
from unittest import mock

import pytest
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
            config.SELENIUM_IMPLICITLY_WAIT
        )
