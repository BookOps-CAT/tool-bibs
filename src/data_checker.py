from src.producer import _barcodes2list
from src.reader import read_data


def verify_barcodes():
    unique_barcodes = set()
    dups = False

    data = read_data()
    for item in data:
        barcodes_lst = _barcodes2list(item.barcode)
        for barcode in barcodes_lst:
            if barcode in unique_barcodes:
                print(f"Found duplicate barcode: {barcode} for {item.t245}")
                dups = True
            else:
                unique_barcodes.add(barcode)

    if not dups:
        print("Success! No duplicate barcodes found.")
