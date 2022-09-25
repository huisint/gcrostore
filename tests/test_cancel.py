from unittest import mock

import crostore

from gcrostore import cancel, config


@mock.patch("crostore.iter_items_to_cancel")
def test_iter_items_to_cancel(iter_items_to_cancel_mock: mock.Mock) -> None:
    items = [mock.Mock(spec_set=crostore.AbstractItem)]
    iter_items_to_cancel_mock.return_value = items
    ms = mock.Mock(spec_set=crostore.AbstractMailSystem)
    ds = mock.Mock(spec_set=crostore.AbstractDataSystem)
    assert list(cancel.iter_items_to_cancel(ms, ds)) == items * len(config.platforms)
