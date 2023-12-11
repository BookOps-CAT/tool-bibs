# tool-bibs
A crosswalk from google sheets to MARC21 for BPL tool library.


## Submission data
BPL's staff submission data is collected in [this spreadsheet](https://docs.google.com/spreadsheets/d/17LM0oVr7ByrbgTzXMPTQRgQPhuoJvI4T84_S3gOEAqc/edit?usp=sharing).

## Setup
This project requires Python 3.10 version.

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies
	+ `pip install -r requirements.txt`

## Verifying submitted data
To verify submitted data does not inlcude any duplicate barcodes run the following command:
`python tool_bibs.py verify`

This command will print out to the terminal any instances of barcodes and associated tool names that were identified as duplicates.

## Running crosswalk
1. Mark new rows in the [submission sheet](https://docs.google.com/spreadsheets/d/17LM0oVr7ByrbgTzXMPTQRgQPhuoJvI4T84_S3gOEAqc/edit?usp=sharing) as "for processing" 
2. Note the last control # in the sheet
3. Activate project's virtual environment
4. Run the following Python command in the CLI (example, the next control # sequence is 24)

`python tool_bibs.py create 24`

5. Mark processed rows in the column "status" as "completed"
6. Add to the sheet new control #s, loaded dates, and Sierra bib #s