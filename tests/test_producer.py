from datetime import date

import pytest

from pymarc import Field, Record
from src.producer import (
    _barcodes2list,
    _convert_price,
    _enforce_trailing_period,
    _enforce_no_trailing_punctuation,
    _date_today,
    _get_item_type_code,
    _make_t001,
    _make_t028,
    _make_t245,
    _make_t246,
    _make_t500,
    _make_t505,
    _make_t520,
    _make_t690,
    _make_t856,
    _make_t960,
    _make_t949,
    _values2list,
    generate_bib,
)

from src.reader import Item


@pytest.mark.parametrize("arg", ["", " ", "\t", "\n"])
def test_barcodes2list_empty_value(arg):
    with pytest.raises(ValueError):
        _barcodes2list(arg)


def test_barcodes2list_invalid_prefix():
    with pytest.raises(ValueError):
        _barcodes2list("14444000000000")


def test_barcodes2list_too_long():
    with pytest.raises(ValueError):
        _barcodes2list("344440000000001")


def test_barcodes2list():
    barcodes = _barcodes2list(" 34444000000000; 34444000000001 ;34444000000002 ")
    assert isinstance(barcodes, list)
    assert len(barcodes) == 3
    assert barcodes[0] == "34444000000000"
    assert barcodes[1] == "34444000000001"
    assert barcodes[2] == "34444000000002"


@pytest.mark.parametrize(
    "arg,expectation",
    [("9", "9.00"), ("149.99", "149.99"), ("7.0", "7.00"), ("0.9", "0.90")],
)
def test_convert_price(arg, expectation):
    assert _convert_price(arg) == expectation


@pytest.mark.parametrize(
    "arg,expectation",
    [
        ("YES", "58"),
        ("yes", "58"),
        ("NO", "59"),
        ("no", "59"),
    ],
)
def test_get_item_type_code(arg, expectation):
    assert _get_item_type_code(arg) == expectation


@pytest.mark.parametrize("arg", ["foo", ""])
def test_get_item_type_code_warnings(arg):
    with pytest.warns(Warning) as warn_msg:
        result = _get_item_type_code(arg)
        assert result == "59"

        if not warn_msg:
            pytest.fail("Expected a warning for invalid loan restriction value")


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


def test_date_today():
    today = _date_today()
    assert isinstance(today, str)
    assert today == date.strftime(date.today(), "%y%m%d")


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


@pytest.mark.parametrize("arg", [5, "5"])
def test_make_t001(arg):
    field = _make_t001(arg)
    assert isinstance(field, Field)
    assert str(field) == "=001  bkl-tll-0000005"


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
def test_make_t505_empty(arg):
    assert _make_t505(arg) is None


@pytest.mark.parametrize(
    "arg, expectation", [("foo ", "Foo"), (" foo. ", "Foo"), ("Foo.", "Foo")]
)
def test_make_t505(arg, expectation):
    field = _make_t505(arg)
    assert isinstance(field, Field)
    assert str(field) == f"=505  8\\$a{expectation}"


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


@pytest.mark.parametrize("arg", ["", " ", "\t", "\n"])
def test_make_t856_empty_value(arg):
    assert _make_t856(arg) == []


def test_make_t856_not_url():
    with pytest.raises(ValueError):
        _make_t856("ftp://example.com")


def test_make_t856_multi():
    fields = _make_t856("https://www.foo.com; https://bar.com")
    assert isinstance(fields, list)
    assert len(fields) == 2

    for f in fields:
        assert isinstance(f, Field)

    assert str(fields[0]) == "=856  42$uhttps://www.foo.com$zTool manual"
    assert str(fields[1]) == "=856  42$uhttps://bar.com$zTool manual"


def test_make_t960_empty():
    with pytest.raises(ValueError):
        _make_t960("", "9.99")


def test_make_t960():
    fields = _make_t960("34444000000000", "9.99", "YES")
    assert isinstance(fields, list)
    assert len(fields) == 1
    assert isinstance(fields[0], Field)
    assert str(fields[0]) == "=960  \\\\$i34444000000000$l41atl$p9.99$q4$t58$ri$sg"


# def test_make_t960_price_formatting():
# fields = _make_t960("34444000000000", , "YES")


def test_make_t949():
    result = _make_t949()
    assert isinstance(result, Field)
    assert str(result) == "=949  \\\\$a*b2=r;"


def test_generate_bib():
    item = Item(
        status="for processing",
        t245="Foo",
        t246="",
        t028="12345",
        t520="spam spam spam",
        t690="Power tools,Garden tools",
        t500="some note",
        t505="bar, shrubbery",
        t856="https://example.com",
        barcode="34444000000000;34444000000001",
        cost="9.99",
        loan_restriction="NO",
    )
    bib = generate_bib(item, 24)

    assert isinstance(bib, Record)
    assert bib["001"].data == "bkl-tll-0000024"
    assert bib["003"].data == "NBPu"
    assert "005" in bib
    assert (
        bib["008"].data
        == f"{date.strftime(date.today(), '%y%m%d')}s20uu    xx                  zxx d"
    )
    assert "028" in bib
    assert str(bib["099"]) == "=099  \\\\$aTOOL"
    assert "245" in bib
    assert "246" not in bib
    assert str(bib["300"]) == "=300  \\\\$a1 tool"
    assert str(bib["336"]) == "=336  \\\\$athree-dimensional form$btdf$2rdacontent"
    assert str(bib["337"]) == "=337  \\\\$aunmediated$bn$2rdamedia"
    assert str(bib["338"]) == "=338  \\\\$aobject$bnr$2rdacarrier"
    notes = bib.get_fields("500")
    assert len(notes) == 1
    assert str(notes[0]) == "=500  \\\\$aSome note"
    assert "505" in bib
    assert "520" in bib
    subjects = bib.get_fields("690")
    assert len(subjects) == 2
    assert "856" in bib
    items = bib.get_fields("960")
    assert len(items) == 2
    assert str(items[1]) == "=960  \\\\$i34444000000001$l41atl$p9.99$q4$t59$ri$sg"
    assert "949" in bib


def test_generate_bib_without_barcodes():
    item = Item(
        status="for processing",
        t245="Foo",
        t246="",
        t028="12345",
        t520="spam spam spam",
        t690="Power tools,Garden tools",
        t500="some note",
        t505="bar, shrubbery",
        t856="https://example.com",
        barcode="",
        cost="9.99",
        loan_restriction="NO",
    )

    with pytest.raises(ValueError) as exc:
        generate_bib(item, 24)
    assert str(exc.value) == "Bib without items: Foo"
