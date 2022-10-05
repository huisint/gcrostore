import contextlib
import json
import typing as t
from collections import abc

import pydantic
from google.auth.transport import requests
from google.oauth2 import credentials
from selenium import webdriver

from gcrostore import config


class User(pydantic.BaseModel):
    name: str
    email: pydantic.EmailStr


class Selenium(pydantic.BaseModel):
    url: pydantic.HttpUrl
    desired_capabilities: dict[str, t.Any]

    @contextlib.contextmanager
    def driver(self) -> abc.Iterator[webdriver.Remote]:
        driver = webdriver.Remote(
            self.url, desired_capabilities=self.desired_capabilities
        )
        driver.implicitly_wait(config.SELENIUM_IMPLICITLY_WAIT)
        try:
            yield driver
        finally:
            driver.quit()


class Google(pydantic.BaseModel):
    creds: dict[str, t.Any]
    sheet_id: str

    @pydantic.validator("creds")
    def creds_is_valid(cls, v: t.Any) -> t.Any:
        creds = credentials.Credentials.from_authorized_user_info(v, config.scopes)
        if not creds.valid and creds.refresh_token:
            creds.refresh(requests.Request())
        return json.loads(creds.to_json())
