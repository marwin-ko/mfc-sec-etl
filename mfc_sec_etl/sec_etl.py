from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import tempfile


# ETL
def load_tickers(fname):
    ext = fname.split('/')[-1].split('.')[-1]
    if ext == 'xlsx':
        df = pd.read_excel(fname)
    elif ext == 'csv':
        df = pd.read_csv(fname)
    df = df.loc[df[df.columns[0]].notnull(), :]
    tickers = df[df.columns[0]].tolist()
    return tickers


def get_soup(ticker, start=0, count=100):
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK={}&owner=exclude&start={}&count={}'.format(ticker, start, count)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_filing(soup, filings=('10-K', '20-F')):
    # filings is ordered by priority
    # So 10k is checked first then so on...
    for filing in filings:
        if soup.find_all("td", text=filing):
            return filing
    if soup.find_all('h1'):
        if soup.find('h1').text == 'No matching Ticker Symbol.':
            return soup.find('h1').text
    else:
        return None


def get_filing_soup(ticker, max_filings=1000, filings=('10-K', '10-Q', '20-F')):
    last_page = None;
    start = 0
    while start < max_filings + 1:
        # add variable time.sleep(np.random()) here...
        soup = get_soup(ticker, start);
        filing = get_filing(soup)
        # log filing if found
        if filing in filings:
            break
        elif filing == 'No matching Ticker Symbol.':
            break
        # check if pages empty
        if last_page == soup.get_text():
            return None, None
        else:
            last_page = soup.get_text()
        # go to next page of reports
        start += 100
    return filing, soup


def get_filing_date(line):
    for sib in line.find_next_siblings('td'):
        if re.search(r'^\d{4}-\d{2}-\d{2}$', sib.text):
            return sib.text
    return None


def get_industry(soup):
    try:
        industry = soup.p.contents[3]
        if industry[:3] == ' - ':
            industry = industry[3:]
        return industry
    except:
        return None


def get_company(soup):
    try:
        if soup.find_all('span'):
            for span in soup.find_all('span'):
                if re.search(r'.+companyName.+', str(span)):
                    company = span.text.split('CIK#:')[0]
                    return company
        else:
            return None
    except:
        return None


def get_xl_url(filing, soup):
    url = 'https://www.sec.gov/Archives/edgar/data/{}/{}/Financial_Report.xlsx'
    if filing in ['10-K', '10-Q', '20-F']:
        td = soup.find("td", text=filing)
        href = td.find_next_sibling('td').find_next('a').attrs['href']
        n1, n2 = re.findall(r'\d+', href)[:2]
        xl_url = url.format(n1, n2)
        fdate = get_filing_date(td)
        return xl_url, fdate
    else:
        return None, None


def get_xl_file(url):
    try:
        tf = tempfile.NamedTemporaryFile(delete=True)
        resp = requests.get(url)
        with open(tf.name, 'wb') as f:
            f.write(resp.content)
        xl_file = pd.ExcelFile(tf.name)
        tf.close()
        return xl_file, 'requests'
    except:
        tf.close()
    return None, 'failed'
