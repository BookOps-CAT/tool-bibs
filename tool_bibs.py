import sys

from src.downloader import get_metadata
from src.producer import save2marc, generate_bib, _date_today
from src.reader import read_data
from src.data_checker import verify_barcodes


def run(start_sequence: str) -> None:
    # refresh local copy of metadata
    get_metadata()
    n = int(start_sequence)

    # determine output file
    date = _date_today()
    out = f"out/tool-bibs-{date}.mrc"

    # loop over metadata, create bibs, and serialize to MARC21
    for item in read_data():
        if item.status == "for processing":
            bib = generate_bib(item, n)
            save2marc(bib, out)
            n += 1

    print("Completed...")
    print(f"Created {n-int(start_sequence)} bibs.")


def verify_data():
    get_metadata()
    verify_barcodes()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 3:
            print("Invalid command. Too many arguments.")
        elif sys.argv[1] == "create":
            run(sys.argv[2])
        elif sys.argv[1] == "verify":
            verify_data()
        else:
            print("Invalid command. Use 'create' or 'verify' argument.")
    except IndexError:
        print("Invalid command. Missing 'create' or 'verify' argument.")
    except ValueError:
        print("Invalid call #. Provide a number after 'create' argument.")
    except Exception as e:
        print(f"A error occurred: {e}.")
