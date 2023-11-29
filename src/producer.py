from datetime import datetime, date
import warnings

from pymarc import Record, Field, Subfield  # type: ignore

from src.reader import Item  # type: ignore


def _barcodes2list(barcodes: str) -> list[str]:
    barcodes_lst = [b.strip() for b in barcodes.split(";") if b.strip()]
    for b in barcodes_lst:
        if not b.startswith("34444"):
            raise ValueError("Invalid barcode.")
        if len(b) != 14:
            raise ValueError("Invalid barcode")

    if not barcodes_lst:
        raise ValueError("Missing barcode(s).")

    return barcodes_lst


def _convert_price(value: str) -> str:
    value_as_float = float(value)
    return f"{value_as_float:.2f}"


def _date_today():
    return date.strftime(date.today(), "%y%m%d")


def _values2list(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


def _enforce_trailing_period(value: str) -> str:
    value = value.strip()
    if value:
        if value.endswith(("!", "?", ".")):
            return value
        else:
            return f"{value}."
    else:
        return value


def _enforce_no_trailing_punctuation(value: str) -> str:
    value = value.strip()
    if value:
        if value.endswith(("!", "?")):
            return value
        elif value.endswith((".", ",", ";")):
            return value[:-1].strip()
        else:
            return value
    else:
        return value


def _get_item_type_code(loan_restriction: str) -> str:
    if loan_restriction.lower() == "yes":
        return "58"
    elif loan_restriction.lower() == "no":
        return "59"
    else:
        warnings.warn("Invalid loan restrition value")
        return "59"


def _make_t001(value: int | str) -> Field:
    sequenceNo = str(value).zfill(7)
    return Field(tag="001", data=f"bkl-tll-{sequenceNo}")


def _make_t028(value: str) -> list[Field]:
    fields = []
    ids = _values2list(value)
    for i in ids:
        fields.append(
            Field(tag="028", indicators=["5", "0"], subfields=[Subfield("a", i)])
        )
    return fields


def _make_t245(value: str) -> Field:
    if value.strip():
        return Field(
            tag="245",
            indicators=["0", "0"],
            subfields=[Subfield("a", f"{value.strip()}")],
        )
    else:
        raise ValueError


def _make_t246(value: str) -> list[Field]:
    fields = []
    alt_titles = _values2list(value)
    for t in alt_titles:
        fields.append(
            Field(
                tag="246",
                indicators=["1", "3"],
                subfields=[Subfield("a", f"{t}")],
            )
        )
    return fields


def _make_t500(value: str) -> list[Field]:
    fields = []
    notes = _values2list(value)
    for n in notes:
        n = _enforce_no_trailing_punctuation(n)
        fields.append(
            Field(
                tag="500",
                indicators=[" ", " "],
                subfields=[Subfield("a", n.capitalize())],
            )
        )
    return fields


def _make_t505(value: str) -> Field:
    if value.strip():
        value = _enforce_no_trailing_punctuation(value)
        return Field(
            tag="505",
            indicators=["8", " "],
            subfields=[Subfield("a", value.capitalize())],
        )
    else:
        return None


def _make_t520(value: str) -> Field:
    value = _enforce_trailing_period(value)
    if value:
        return Field(
            tag="520",
            indicators=[" ", " "],
            subfields=[Subfield("a", f"{value.capitalize()}")],
        )
    else:
        return None


def _make_t690(value: str) -> list[Field]:
    """
    No need to enfore punctuation since the values are controlled
    by the sheet.
    """
    fields = []
    subjects = [v.strip() for v in value.split(",") if v.strip()]
    for s in subjects:
        fields.append(
            Field(
                tag="690",
                indicators=[" ", "4"],
                subfields=[Subfield("a", f"{s}.")],
            )
        )
    if not fields:
        raise Warning("No subjects tags were provided.")
    return fields


def _make_t856(value: str, label: str) -> list[Field]:
    fields = []
    urls = _values2list(value)
    for u in urls:
        if not u.startswith("https://"):
            raise ValueError
        fields.append(
            Field(
                tag="856",
                indicators=["4", "2"],
                subfields=[
                    Subfield("u", u.strip()),
                    Subfield("z", label),
                ],
            )
        )
    return fields


def _make_t960(
    barcodes: str, cost: str, loan_restriction: str = "NO", status: str = "g"
) -> list[Field]:
    fields = []
    barcodes_lst = _barcodes2list(barcodes)

    item_type_code = _get_item_type_code(loan_restriction)
    formatted_cost = _convert_price(cost)

    for barcode in barcodes_lst:
        fields.append(
            Field(
                tag="960",
                indicators=[" ", " "],
                subfields=[
                    Subfield("i", barcode),
                    Subfield("l", "41atl"),
                    Subfield("p", formatted_cost),
                    Subfield("q", "4"),  # stat code: 4 - undefined
                    Subfield("t", item_type_code),  # item type: 25 - realia
                    Subfield("r", "i"),  # item format: i - adult other
                    Subfield("s", status),
                ],
            )
        )
    return fields


def _make_t949():
    return Field(tag="949", indicators=[" ", " "], subfields=[Subfield("a", "*b2=r;")])


def generate_bib(item: Item, control_no_sequence: int) -> Record:
    bib = Record()
    bib.leader = "00000nrm a2200000M  4500"

    # 001
    controlNoTag = _make_t001(control_no_sequence)
    bib.add_ordered_field(controlNoTag)

    # 003
    bib.add_ordered_field(Field(tag="003", data="NBPu"))

    # 005
    bib.add_ordered_field(
        Field(tag="005", data=datetime.strftime(datetime.now(), "%y%m%d%H%M%S.%f"))
    )

    # 008
    today = _date_today()
    bib.add_ordered_field(
        Field(tag="008", data=f"{today}s20uu    xx                ||zxx d")
    )

    # 028
    skus = _make_t028(item.t028)
    for s in skus:
        bib.add_ordered_field(s)

    # 099
    bib.add_ordered_field(
        Field(tag="099", indicators=[" ", " "], subfields=[Subfield("a", "TOOL")])
    )

    # 245
    title_field = _make_t245(item.t245)
    bib.add_ordered_field(title_field)

    # 246
    alt_titles = _make_t246(item.t246)
    for a in alt_titles:
        bib.add_ordered_field(a)

    # 300 field
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
    notes_general = _make_t500(item.t500)
    for n in notes_general:
        bib.add_ordered_field(n)

    # 505
    note_content = _make_t505(item.t505)
    if note_content:
        bib.add_ordered_field(_make_t505(item.t505))

    # 520
    summary = _make_t520(item.t520)
    if summary:
        bib.add_ordered_field(_make_t520(item.t520))

    # 690
    subjects = _make_t690(item.t690)
    for s in subjects:
        bib.add_ordered_field(s)

    # 856 with manual url
    urls = _make_t856(item.t856, "Tool manual")
    for u in urls:
        bib.add_ordered_field(u)

    program_url_tag = _make_t856(
        "https://www.bklynlibrary.org/tool-library", "Tool library webpage"
    )
    bib.add_ordered_field(program_url_tag[0])

    # item records 960s
    try:
        items = _make_t960(item.barcode, item.cost, item.loan_restriction)
    except ValueError:
        raise ValueError(f"Bib without items: {item.t245}")

    for i in items:
        bib.add_ordered_field(i)

    # command tag 949
    command_tag = _make_t949()
    bib.add_ordered_field(command_tag)

    return bib


def save2marc(bib: Record, fh_out: str) -> None:
    """Appends MARC21 record to a file"""
    with open(fh_out, "ab") as out:
        out.write(bib.as_marc())
