import pathlib
import smtplib
import typing as t
from email.mime import base, text

import crostore
import jinja2
import markdown

from gcrostore import config, models

MESSAGEDIR = pathlib.Path(__file__).parent / "messages"


def get_jinja2_env() -> jinja2.Environment:
    return jinja2.Environment(loader=jinja2.FileSystemLoader(MESSAGEDIR))


def get_template(name: str) -> jinja2.Template:
    env = get_jinja2_env()
    return env.get_template(name)


def render_markdown_template(template_name: str, *args: t.Any, **kwargs: t.Any) -> str:
    template = get_template(template_name)
    html_text = markdown.markdown(template.render(*args, **kwargs))
    return html_text


def send_message(message: base.MIMEBase) -> None:
    message["from"] = config.SMTP_FROM
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as smtp:
        smtp.send_message(message)


def build_cancellation_success_message(
    user: models.User,
    item: crostore.AbstractItem,
) -> text.MIMEText:
    body = render_markdown_template(
        "cancellation_success.md.j2",
        user_name=user.name or user.email,
        crostore_id=item.crostore_id,
        platform_name=item.platform.name,
        item_id=item.item_id,
        selling_page_url=item.selling_page_url,
    )
    message = text.MIMEText(body, "html")
    message["to"] = user.email
    message["subject"] = "【Crostore】出品取り消し"
    return message


def notify_cancellation_success(user: models.User, item: crostore.AbstractItem) -> None:
    message = build_cancellation_success_message(user, item)
    send_message(message)


def build_cancellation_failure_message(
    user: models.User, item: crostore.AbstractItem, error_message: str = ""
) -> text.MIMEText:
    body = render_markdown_template(
        "cancellation_failure.md.j2",
        user_name=user.name or user.email,
        crostore_id=item.crostore_id,
        platform_name=item.platform.name,
        item_id=item.item_id,
        selling_page_url=item.selling_page_url,
        error=error_message,
    )
    message = text.MIMEText(body, "html")
    message["to"] = user.email
    message["subject"] = "【Crostore】出品取り消し（失敗）"
    return message


def notify_cancellation_failure(
    user: models.User, item: crostore.AbstractItem, error_message: str = ""
) -> None:
    message = build_cancellation_failure_message(user, item, error_message)
    send_message(message)


def build_request_relogin_message(
    user: models.User, platform: crostore.AbstractPlatform, selenium: models.Selenium
) -> text.MIMEText:
    body = render_markdown_template(
        "relogin_request.md.j2",
        user_name=user.name or user.email,
        platform_name=platform.name,
        relogin_url="Sorry not implemented",  # TODO: Implement it
    )
    message = text.MIMEText(body, "html")
    message["to"] = user.email
    message["subject"] = f"【Crostore】再ログインのお願い（{platform.name}）"
    return message


def request_relogin(
    user: models.User, platform: crostore.AbstractPlatform, selenium: models.Selenium
) -> None:
    message = build_request_relogin_message(user, platform, selenium)
    send_message(message)
