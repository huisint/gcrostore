from __future__ import annotations

import base64
import dataclasses
import functools
import logging
import typing as t
from collections import abc

import crostore
from google.oauth2 import credentials
from googleapiclient import discovery

logger = logging.getLogger(__name__)


@functools.singledispatch
def get_sold_mail_query(platform: crostore.AbstractPlatform) -> str:
    raise ValueError(f"Unsupported platform: {platform}")


@get_sold_mail_query.register
def _(platform: crostore.platforms.mercari.Platform) -> str:
    return f'from:({platform.email}) AND "購入しました"'


@get_sold_mail_query.register
def _(platform: crostore.platforms.yahoo_auction.Platform) -> str:
    return f"from:({platform.email})" + ' AND {subject:("ヤフオク! - 終了（落札者あり）")}'


@dataclasses.dataclass(frozen=True)
class GmailMailSystem(crostore.AbstractMailSystem):
    creds: credentials.Credentials
    user_id: str = "me"
    done_label_name: str = "crostored"

    def iter_sold_messages(
        self, platform: crostore.AbstractPlatform
    ) -> abc.Generator[crostore.AbstractMessage, None, None]:
        gmailapi = self.get_gmailapi()
        for sold_message_id in self.iter_sold_message_ids(platform):
            gmail_message = (
                gmailapi.users()
                .messages()
                .get(
                    userId=self.user_id,
                    id=sold_message_id,
                )
                .execute()
            )
            payload = gmail_message["payload"]
            headers = {header["name"]: header["value"] for header in payload["headers"]}
            try:
                subject = headers.get("subject", "")
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
                yield platform.create_message(subject, body)
            except Exception as err:
                logger.error(f"Cannot deal with {gmail_message}: {err}")

    def get_gmailapi(self, **kwargs: t.Any):  # type: ignore[no-untyped-def]
        gmailapi = discovery.build("gmail", "v1", credentials=self.creds, **kwargs)
        return gmailapi

    def get_donelabel(self, label_name: str):  # type: ignore[no-untyped-def]
        gmailapi = self.get_gmailapi()
        labels = (
            gmailapi.users()
            .labels()
            .list(userId=self.user_id)
            .execute()
            .get("labels", list())
        )
        donelabels = [label for label in labels if label.get("name", "") == label_name]
        assert len(donelabels) <= 1, "The number of donelabels should be 1 or less"
        if donelabels:
            donelabel = donelabels[0]
        else:
            donelabel = (
                gmailapi.users()
                .labels()
                .create(userId=self.user_id, body=dict(name=label_name))
                .execute()
            )
        logger.debug(f"Got {donelabel} as a done-label")
        return donelabel

    def iter_sold_message_ids(
        self,
        platform: crostore.AbstractPlatform,
    ) -> abc.Generator[str, None, None]:
        gmailapi = self.get_gmailapi()
        done_label = self.get_donelabel(self.done_label_name)
        sold_mail_query = get_sold_mail_query(platform)
        messages = (
            gmailapi.users()
            .messages()
            .list(
                userId=self.user_id,
                q=sold_mail_query + " AND -{label:" + self.done_label_name + "}",
            )
            .execute()
            .get("messages", list())
        )
        for message in messages:
            yield str(message.get("id", ""))
            gmailapi.users().messages().modify(
                userId=self.user_id,
                id=str(message.get("id", "")),
                body=dict(addLabelIds=[str(done_label.get("id", ""))]),
            ).execute()
            logger.info(f"Added {done_label} to {message}")
