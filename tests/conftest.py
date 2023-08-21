import pytest

from src.reader import Item


@pytest.fixture
def fake_item():
    return Item(
        "",
        "Foo",
        "Alt-Foo",
        "1234",
        "spam",
        "Hand Tool",
        "some note",
        "one, two, three",
        "",
        "34444000000000",
        "9.99",
    )
