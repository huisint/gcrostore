import dataclasses
import logging
import typing as t
from collections import abc

import crostore
from google.oauth2 import credentials
from googleapiclient import discovery

from gcrostore import config

logger = logging.getLogger(__name__)

CROSTORE_ID_COLUMN = 0
"""The column number of Crostore ID in Google Sheets."""
COLUMN_OFFSET = 3
"""The column number that platform ID columns starts from in Google Sheets."""


def get_platform_column(platform: crostore.AbstractPlatform) -> int:
    return config.platforms.index(platform) + COLUMN_OFFSET


@dataclasses.dataclass(frozen=True)
class SheetsDataSystem(crostore.AbstractDataSystem):
    creds: credentials.Credentials
    sheet_id: str
    sheet_name: str = "data"
    user_id: str = "me"

    def iter_related_items(
        self, item: crostore.AbstractItem
    ) -> abc.Generator[crostore.AbstractItem, None, None]:
        values = self.get_values()
        try:
            index = values[get_platform_column(item.platform)].index(item.item_id)
        except ValueError:
            logger.warn(f"{item} is not registered")
            return
        for i, platform in enumerate(config.platforms):
            if platform == item.platform:
                continue
            item_id = values[i + COLUMN_OFFSET][index]
            crostore_id = values[CROSTORE_ID_COLUMN][index]
            yield platform.create_item(item_id, crostore_id)

    def get_values(self) -> list[list[t.Any]]:
        sheetsapi = self.get_sheetsapi()
        values = (
            sheetsapi.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.sheet_id,
                range=self.sheet_name,
                majorDimension="COLUMNS",
            )
            .execute()
            .get("values", [[]])
        )
        return [list(value) for value in values]

    def get_sheetsapi(self, **kwargs: t.Any):  # type: ignore[no-untyped-def]
        sheetsapi = discovery.build("sheets", "v4", credentials=self.creds, **kwargs)
        return sheetsapi

    def update(self, item: crostore.AbstractItem) -> None:
        if not item.crostore_id:
            raise ValueError(f"crostore_id is empty in item: {item}")
        index = int(
            item.crostore_id.rstrip("c")
        )  # TODO: Define crostore_id format in a different place
        sheetsapi = self.get_sheetsapi()
        _range = f"{self.sheet_name}!{chr(get_platform_column(item.platform) + 65)}{index + 2}"  # A1 annotation
        sheetsapi.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=_range,
            body=dict(range=_range, majorDimension="COLUMNS", values=[[item.item_id]]),
        ).execute()

    def delete(self, item: crostore.AbstractItem) -> None:
        if not item.crostore_id:
            raise ValueError(f"crostore_id is empty in item: {item}")
        index = int(
            item.crostore_id.rstrip("c")
        )  # TODO: Define crostore_id format in a different place
        sheetsapi = self.get_sheetsapi()
        _range = f"{self.sheet_name}!{chr(get_platform_column(item.platform) + 65)}{index + 2}"  # A1 annotation
        sheetsapi.spreadsheets().values().clear(
            spreadsheetId=self.sheet_id,
            range=_range,
            body=dict(),
        ).execute()
