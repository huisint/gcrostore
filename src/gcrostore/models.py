import json
import typing as t

import pydantic
from crostore import config as crostore_config
from google.auth.transport import requests
from google.oauth2 import credentials
from selenium import webdriver
from selenium.webdriver.common import options

from gcrostore import config


class User(pydantic.BaseModel):
    name: str
    email: pydantic.EmailStr


class Selenium(pydantic.BaseModel):
    url: pydantic.HttpUrl
    desired_capabilities: dict[str, t.Any]

    def model_post_init(self, __context: t.Any) -> None:
        self._options = options.ArgOptions()
        for key, value in self.desired_capabilities.items():
            self._options.set_capability(key, value)

    @property
    def options(self) -> options.ArgOptions:
        return self._options

    def driver(self) -> webdriver.Remote:
        driver = webdriver.Remote(
            command_executor=str(self.url),
            options=self.options,
        )
        driver.implicitly_wait(crostore_config.SELENIUM_WAIT)
        return driver


class Google(pydantic.BaseModel):
    creds: dict[str, t.Any]
    sheet_id: str

    @pydantic.field_validator("creds")
    def creds_is_valid(cls, v: t.Any) -> t.Any:
        creds = credentials.Credentials.from_authorized_user_info(v, config.scopes)
        if not creds.valid and creds.refresh_token:
            creds.refresh(requests.Request())
        return json.loads(creds.to_json())
