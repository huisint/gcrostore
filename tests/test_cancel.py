import crostore
import pytest_mock

from gcrostore import cancel, config


def test_iter_items_to_cancel(mocker: pytest_mock.MockerFixture) -> None:
    items = [mocker.Mock(spec_set=crostore.AbstractItem)]
    mocker.patch("crostore.iter_items_to_cancel", return_value=items)
    ms = mocker.Mock(spec_set=crostore.AbstractMailSystem)
    ds = mocker.Mock(spec_set=crostore.AbstractDataSystem)
    assert list(cancel.iter_items_to_cancel(ms, ds)) == items * len(config.platforms)
