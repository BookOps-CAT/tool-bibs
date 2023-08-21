from pymarc import Record
from src.producer import generate_bib


def test_generate_bib(fake_item):
    bib = generate_bib(fake_item, 1)
    assert isinstance(bib, Record)
    assert bib["001"].data == "bkl-tll-0000001"
