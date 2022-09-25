from unittest import mock

import crostore
import jinja2
import pytest

from gcrostore import config, mail, models
from tests import FixtureRequest


def test_get_jinja2_env() -> None:
    env = mail.get_jinja2_env()
    loader = env.loader
    assert isinstance(loader, jinja2.FileSystemLoader)
    assert loader.searchpath == [str(mail.MESSAGEDIR)]


@pytest.mark.parametrize("name", [path.name for path in mail.MESSAGEDIR.glob("*.j2")])
def test_get_template(name: str) -> None:
    template = mail.get_template(name)
    assert template.filename == str(mail.MESSAGEDIR / name)


@pytest.mark.parametrize("title", ["Title"])
@pytest.mark.parametrize("description", ["Markdown template test"])
@pytest.mark.parametrize("items", [[f"item{i}" for i in range(3)]])
@mock.patch("gcrostore.mail.get_template")
def test_render_markdown_template(
    get_template_mock: mock.Mock,
    title: str,
    description: str,
    items: list[str],
) -> None:
    markdown_text = (
        "## {{ title }}\n"
        "{{ description }}\n\n"
        "{% for item in items %}\n"
        "- {{ item }}\n"
        "{% endfor %}\n"
    )
    template = jinja2.Template(markdown_text)
    get_template_mock.return_value = template
    html_text = mail.render_markdown_template(
        "template_name",
        {"title": title},
        description=description,
        items=items,
    )
    assert (
        html_text
        == f"<h2>{title}</h2>\n<p>Markdown template test</p>\n"
        + "<ul>\n"
        + "".join([f"<li>\n<p>{item}</p>\n</li>\n" for item in items])
        + "</ul>"
    )


@pytest.fixture(params=["foo", "bar"])
def user(request: FixtureRequest[str]) -> models.User:
    name = request.param
    return models.User(name=name, email=f"{name}@example.com")


@pytest.fixture(params=config.platforms)
def item(request: FixtureRequest[crostore.AbstractPlatform]) -> crostore.AbstractItem:
    return request.param.create_item("m000000000", "c00000")


@pytest.fixture(params=["http://example.com:4444/wd/hub"])
def selenium(request: FixtureRequest[str]) -> models.Selenium:
    return models.Selenium(url=request.param, desired_capabilities=dict())


def test_build_cancellation_success_message(
    user: models.User, item: crostore.AbstractItem
) -> None:
    message = mail.build_cancellation_success_message(user, item)
    assert message.get_content_subtype() == "html"
    assert message["to"] == user.email
    assert message["subject"] == "【Crostore】出品取り消し"


def test_build_cancellation_failure_message(
    user: models.User, item: crostore.AbstractItem
) -> None:
    message = mail.build_cancellation_failure_message(user, item)
    assert message.get_content_subtype() == "html"
    assert message["to"] == user.email
    assert message["subject"] == "【Crostore】出品取り消し（失敗）"


@pytest.mark.parametrize("platform", config.platforms)
def test_build_request_relogin_message(
    user: models.User, platform: crostore.AbstractPlatform, selenium: models.Selenium
) -> None:
    message = mail.build_request_relogin_message(user, platform, selenium)
    assert message.get_content_subtype() == "html"
    assert message["to"] == user.email
    assert message["subject"] == f"【Crostore】再ログインのお願い（{platform.name}）"
