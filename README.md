# U.S. Securities and Exchange Commission Extract Transform Load
Custom data pull from U.S. Securities and Exchange Commission (SEC) for anonymous investment company.


## Requirements
- [GitHub](https://git-scm.com/downloads)
- [Python 3](https://www.anaconda.com/distribution/)
    - The link is for anaconda, but feel free to download Python 3 however you want.


## Windows Installation
1. Download the following: 
    - [Cygwin](https://www.cygwin.com)
2. Using Cygwin, clone this git repository with the command below:
    - `git clone https://github.com/marwin-ko/mfc-sec-etl.git`


## OSX or Linux Installation
1. In the terminal, clone this git repository with the command below:
 - `git clone https://github.com/marwin-ko/mfc-sec-etl.git`


## Run SEC ETL
1. Put list of tickers in `./mfc_sec_etl/sourcedata/`.
    - CSV and EXCEL formats are acceptable.
    - File must be single column at first column position.
    - Column header can be title anything.
2. Change directory to `./mfc_sec_etl` (top level of this repo).
3. Run code using the following command: `python3 ./mfc_sec_etl/runner.py -f <file_name.csv>`
    - Run test file: `python3 ./mfc_sec_etl/runner.py -f test_tickers.csv`
    - Run single ticker test: `python3 ./mfc_sec_etl/runner.py -t`
4. The ticker information is stored as a csv file in `./mfc_sec_etl/results/`
    - File will be saved as input file name with date appended to it: `<file_name>__yyyy_mm_dd.csv`
        - Example: `test_tickers__2019_11_05.csv`.
    - If ETL is run twice on the same ticker on the same day, a new file with `_copy` append will be created to preserve the first file.
        - Example: `test_tickers__2019_11_05_copy.csv`.
    - If ETL is run 3+ times on the same day, then the copy file (e.g. `test_tickers__2019_11_05_copy.csv`) will be written over. 
