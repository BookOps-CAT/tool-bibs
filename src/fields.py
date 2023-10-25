from datetime import date

from pymarc import Field, Subfield


def _barcodes2list(barcodes: str) -> list[str]:
    barcodes_lst = [str(int(b.strip())) for b in barcodes.split(";") if b.strip()]
    for b in barcodes_lst:
        if not b.startswith("34444"):
            raise ValueError("Invalid barcode.")
        if len(b) != 14:
            raise ValueError("Invalid barcode")

    if not barcodes_lst:
        raise ValueError("Missing barcode(s).")

    return barcodes_lst


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
                indicators=[" ", "7"],
                subfields=[Subfield("a", f"{s}."), Subfield("2", "bookops")],
            )
        )
    if not fields:
        raise Warning("No subjects tags were provided.")
    return fields


def _make_t856(value: str) -> list[Field]:
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
                    Subfield("z", "Tool manual"),
                ],
            )
        )
    return fields


def _make_t960(barcodes: str, cost: str, status: str = "g") -> list[Field]:
    fields = []
    barcodes = _barcodes2list(barcodes)
    for barcode in barcodes:
        fields.append(
            Field(
                tag="960",
                indicators=[" ", " "],
                subfields=[
                    Subfield("i", barcode),
                    Subfield("l", "41a  "),
                    Subfield("p", cost),
                    Subfield("q", "4"),  # stat code: 4 - undefined
                    Subfield("t", "25"),  # item type: 25 - realia
                    Subfield("r", "i"),  # item format: i - adult other
                    Subfield("s", status),
                ],
            )
        )
    return fields
