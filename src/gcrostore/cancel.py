import logging
from collections import abc

import crostore
from google.oauth2 import credentials

from gcrostore import api_version, app, config, mail, models

logger = logging.getLogger(__name__)


def iter_items_to_cancel(
    ms: crostore.AbstractMailSystem, ds: crostore.AbstractDataSystem
) -> abc.Generator[crostore.AbstractItem, None, None]:
    for platform in config.platforms:
        for item in crostore.iter_items_to_cancel(platform, ms, ds):
            yield item


@app.post(f"/{api_version}/cancel/all")
def execute_cancellation(
    user: models.User, selenium: models.Selenium, google: models.Google
) -> None:
    creds = credentials.Credentials.from_authorized_user_info(google.creds)
    ms = crostore.mailsystems.gmail.GmailMailSystem(creds)
    ds = crostore.datasystems.google_sheets.GoogleSheetsDataSystem(
        creds, google.sheet_id, config.platforms
    )
    with selenium.driver() as driver:
        for item in iter_items_to_cancel(ms, ds):
            try:
                item.cancel(driver)
                mail.notify_cancellation_success(user, item)
            except crostore.exceptions.ItemNotCanceledError as err:
                logger.error(f"Failed canceling {item}: {err}")
                mail.notify_cancellation_failure(user, item)
