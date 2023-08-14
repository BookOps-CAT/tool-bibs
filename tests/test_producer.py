import pytest

from pymarc import Field
from src.producer import (
    _enforce_trailing_period,
    _enforce_no_trailing_punctuation,
    _make_t028,
    _make_t245,
    _make_t246,
    _make_t500,
    _make_t520,
    _make_t690,
    _values2list,
    generate_bib,
)


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("", ""),
        (" ", ""),
        ("\t", ""),
        ("\n", ""),
        ("foo", "foo."),
        (" foo ", "foo."),
        (" foo!", "foo!"),
        ("foo? ", "foo?"),
        ("foo.", "foo."),
    ],
)
def test_enforce_trailing_period(arg, expectation):
    assert _enforce_trailing_period(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("", ""),
        (" ", ""),
        ("\t", ""),
        ("\n", ""),
        ("foo", "foo"),
        (" foo ", "foo"),
        (" foo!", "foo!"),
        ("foo? ", "foo?"),
        ("foo,", "foo"),
        ("foo ;", "foo"),
    ],
)
def test_enforce_no_trailing_punctuation(arg, expectation):
    assert _enforce_no_trailing_punctuation(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("foo", ["foo"]),
        (" foo ", ["foo"]),
        (" foo; bar ", ["foo", "bar"]),
        ("foo;bar ; spam ", ["foo", "bar", "spam"]),
        ("", []),
        (" ", []),
        ("\n", []),
        ("\t", []),
    ],
)
def test_values2list(arg, expectation):
    assert _values2list(arg) == expectation


@pytest.mark.parametrize("arg", ["", " ", "\n", "\t"])
def test_make_t028_empty(arg):
    assert _make_t028(arg) == []


def test_make_t028_single_sku():
    fields = _make_t028(" 12345 ")
    assert isinstance(fields, list)
    assert len(fields) == 1
    assert isinstance(fields[0], Field)
    assert str(fields[0]) == "=028  50$a12345"


def test_make_t028_multi_sku():
    fields = _make_t028("12345; 2345A")
    assert len(fields) == 2
    for f in fields:
        assert isinstance(f, Field)

    assert str(fields[0]) == "=028  50$a12345"
    assert str(fields[1]) == "=028  50$a2345A"


@pytest.mark.parametrize("arg", ["", " ", "\n", "\t"])
def test_make_t245_empty_value(arg):
    with pytest.raises(ValueError):
        _make_t245(arg)


def test_make_t245():
    field = _make_t245(" Foo Bar ")
    assert isinstance(field, Field)
    assert str(field) == "=245  00$aFoo Bar"


@pytest.mark.parametrize("arg", ["", " ", "\t", "\n"])
def test_make_t246_empty_value(arg):
    assert _make_t246(arg) == []


def test_make_t246_single_alt():
    fields = _make_t246(" Foo")
    assert isinstance(fields, list)
    assert isinstance(fields[0], Field)
    assert str(fields[0]) == "=246  13$aFoo"


def test_make_t246_multi_alt():
    fields = _make_t246("Foo ; Bar;Spam\n")
    assert isinstance(fields, list)
    assert len(fields) == 3
    for f in fields:
        assert isinstance(f, Field)

    assert str(fields[0]) == "=246  13$aFoo"
    assert str(fields[1]) == "=246  13$aBar"
    assert str(fields[2]) == "=246  13$aSpam"


@pytest.mark.parametrize("arg", ["", " ", "\t", "\n"])
def test_make_t500_empty_value(arg):
    assert _make_t500(arg) == []


def test_make_t500_single():
    fields = _make_t500("foo.")
    assert isinstance(fields, list)
    assert len(fields) == 1
    assert isinstance(fields[0], Field)
    assert str(fields[0]) == "=500  \\\\$aFoo"


def test_make_t500_multi():
    fields = _make_t500("foo,; bar.")
    assert isinstance(fields, list)
    assert len(fields) == 2
    assert str(fields[0]) == "=500  \\\\$aFoo"
    assert str(fields[1]) == "=500  \\\\$aBar"


@pytest.mark.parametrize("arg", ["", " ", "\t", "\n"])
def test_make_t520_empty_value(arg):
    assert _make_t520(arg) is None


@pytest.mark.parametrize(
    "arg,expectation",
    [
        (" foo bar ", "Foo bar."),
        ("Foo bar!", "Foo bar!"),
        ("Foo bar?", "Foo bar?"),
        (" foo bar. ", "Foo bar."),
    ],
)
def test_make_t520(arg, expectation):
    field = _make_t520(arg)
    assert isinstance(field, Field)
    assert str(field) == f"=520  \\\\$a{expectation}"


def test_make_t690_empty_value():
    with pytest.raises(Warning):
        _make_t690("")


def test_make_t690():
    fields = _make_t690("Foo, Bar")
    assert isinstance(fields, list)
    assert len(fields) == 2
    for f in fields:
        assert isinstance(f, Field)

    assert str(fields[0]) == "=690  \\7$aFoo.$2bookops"
    assert str(fields[1]) == "=690  \\7$aBar.$2bookops"
