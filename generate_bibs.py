import sys

from src.downloader import get_metadata
from src.producer import save2marc, generate_bib, _date_today
from src.reader import read_data


def run(start_sequence: int) -> None:
    # refresh local copy of metadata
    get_metadata()
    n = int(start_sequence)

    # determine output file
    date = _date_today()
    out = f"out/tool-bibs-{date}.mrc"

    # loop over metadata, create bibs, and serialize to MARC21
    for item in read_data():
        if item.status == "for processing":
            bib = generate_bib(item, start_sequence)
            save2marc(bib, out)
            n += 1


if __name__ == "__main__":
    run(sys.argv[1])
