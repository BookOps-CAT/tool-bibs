from datetime import datetime, date

from pymarc import Record, Field, Subfield

from src.reader import Item, read_data
from src.fields import (
    _date_today,
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
)


def generate_bib(item: Item, control_no_sequence: int) -> Record:
    bib = Record()
    bib.leader = "00000nrm a2200000M  4500"

    # 001
    controlNoTag = _make_t001(control_no_sequence)
    bib.add_field(controlNoTag)

    # 005
    bib.add_ordered_field(
        Field(tag="005", data=datetime.strftime(datetime.now(), "%y%m%d%H%M%S.%f"))
    )

    # 008
    today = _date_today()
    bib.add_ordered_field(
        Field(tag="008", data=f"{today}s20uu    xx                  zxx d")
    )

    # 028
    skus = _make_t028(item.t028)
    bib.add_ordered_field(*skus)

    # 099
    bib.add_ordered_field(
        Field(tag="099", indicators=[" ", " "], subfields=[Subfield("a", "TOOL")])
    )

    # 245
    bib.add_ordered_field(_make_t245(item.t245))

    # 246
    alt_titles = _make_t246(item.t246)
    bib.add_ordered_field(*alt_titles)

    # 300
    bib.add_ordered_field(
        Field(tag="300", indicators=[" ", " "], subfields=[Subfield("a", "1 tool")])
    )

    # RDA 3xx tags
    bib.add_ordered_field(
        Field(
            tag="336",
            indicators=[" ", " "],
            subfields=[
                Subfield("a", "three-dimensional form"),
                Subfield("b", "tdf"),
                Subfield("2", "rdacontent"),
            ],
        )
    )
    bib.add_ordered_field(
        Field(
            tag="337",
            indicators=[" ", " "],
            subfields=[
                Subfield("a", "unmediated"),
                Subfield("b", "n"),
                Subfield("2", "rdamedia"),
            ],
        )
    )
    bib.add_ordered_field(
        Field(
            tag="338",
            indicators=[" ", " "],
            subfields=[
                Subfield("a", "object"),
                Subfield("b", "nr"),
                Subfield("2", "rdacarrier"),
            ],
        )
    )

    # 500
    notes = _make_t500(item.t500)
    bib.add_ordered_field(*notes)

    # 505
    bib.add_ordered_field(_make_t505(item.t505))

    # 520
    bib.add_ordered_field(_make_t520(item.t520))

    # 690
    subjects = _make_t690(item.t690)
    bib.add_ordered_field(*subjects)

    # 856
    urls = _make_t856(item.t856)
    bib.add_ordered_field(*urls)

    # 960
    items = _make_t960(
        item.barcode,
        item.cost,
    )
    bib.add_ordered_field(*items)

    # 949 command line
    bib.add_ordered_field(
        Field(tag="949", indicators=[" ", " "], subfields=[Subfield("a", "*b2=o;")])
    )

    return bib


# def
