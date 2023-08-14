from pymarc import Record, Field, Subfield

from src.reader import Item


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


def _make_t001(value: int) -> Field:
    pass


def generate_bib(item: Item, control_no_sequence: int) -> Record:
    bib = Record()
    bib.leader = ""
    bib.add_ordered_field()
    bib.add_ordered_field(_make_t245(item.title))
    alt_titles = _make_t246(item.t246)
    for a in alt_titles:
        bib.add_ordered_field(a)
    skus = _make_t028(item.t028)
    for s in skus:
        bib.add_ordered_field(s)
