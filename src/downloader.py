import pandas as pd


SHEET_ID = "17LM0oVr7ByrbgTzXMPTQRgQPhuoJvI4T84_S3gOEAqc"
SHEET_NAME = "metadata"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
COL_NAMES = [
    "status",
    "t245",
    "t246",
    "t028",
    "t520",
    "t690",
    "t500",
    "t505",
    "t856",
    "barcode",
    "cost",

]


def get_metadata():
    df = pd.read_csv(URL, usecols=range(1, 12), names=COL_NAMES, skiprows=[0])
    df.to_csv("out/metadata.csv", index=False)
