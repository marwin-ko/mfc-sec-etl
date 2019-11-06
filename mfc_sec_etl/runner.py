import argparse
import numpy as np
import os
import pandas as pd
from random import random
from sec_etl import *
from reports.cash_flow.etl import wrapper_get_cashflow_df_and_col
from reports.cash_flow.investing_activity import wrapper_get_ia_values_and_label
from reports.cash_flow.operating_activity import wrapper_get_oa_values_and_label
from reports.document_entity_information.total_outstanding_shares import get_total_outstanding_shares
import time
from utils import is_current_dir_correct, make_cashflow_colnames, update_dict_with_cashflow_vals, get_save_path


parser = argparse.ArgumentParser(description='SEC runner script.')
parser.add_argument('-f', action='store', dest='fname', type=str, default=str)
parser.add_argument('-t', action='store_true', dest='test', default=False)
args = parser.parse_args()


fname = f'./sourcedata/{args.fname}'


if not os.path.exists(fname):
    assert False, 'ERROR: This file path does not exist.'


if not is_current_dir_correct():
    assert False, 'ERROR: You are in the wrong directory. You should be in */mfc-sec-etl/*'


# Run Test
if args.test:
    tickers = ['GNC']
else:
    tickers = load_tickers(fname)


investing_colnames = make_cashflow_colnames('investing')
operating_colnames = make_cashflow_colnames('operating')


# init dict to store results
info_dict = {k: [] for k in ('ticker',
                             'company',
                             'industry',
                             'filing_type',
                             'filing_date',
                             'dler_info',
                             'total_outstanding_shares',
                             'investing_activity_label',
                             *investing_colnames,
                             'operating_activity_label',
                             *operating_colnames,)}


for i, ticker in enumerate(tickers, 1):
    # Meta + Excel File ETL
    filing, soup = get_filing_soup(ticker)
    company = get_company(soup)
    industry = get_industry(soup)
    xl_url, fdate = get_xl_url(filing, soup)
    xl_file, dler_info = get_xl_file(xl_url)


    # Print ticker info in command line
    nl = '\n'
    print(f'#: {i}{nl}'
          f'TICKER: {ticker}{nl}'
          f'COMPANY: {company}{nl}'
          f'INDUSTRY: {industry}{nl}'
          f'FILING: {filing}{nl}'
          f'FDATE: {fdate}')


    # random sleep ~0.5 second per ticker. ~120 tickers per min
    time.sleep(random()/2)


    # change to results dict
    info_dict['ticker'].append(ticker)
    info_dict['company'].append(company)
    info_dict['industry'].append(industry)
    info_dict['filing_type'].append(filing)
    info_dict['filing_date'].append(fdate)
    info_dict['dler_info'].append(dler_info)


    if xl_file and filing == '10-K':
        # get & log TOTAL OUTSTANDING SHARES (possible to log nan)
        total_outstanding_shares = get_total_outstanding_shares(xl_file)
        info_dict['total_outstanding_shares'].append(total_outstanding_shares)

        # ETL cashflow data
        cashflow_df, cashflow_col = wrapper_get_cashflow_df_and_col(xl_file)
        if (cashflow_df is None) or (cashflow_col is None):
            # log INVESTING ACTIVITIES
            info_dict['investing_activity_label'].append(np.nan)
            info_dict = update_dict_with_cashflow_vals(info_dict,
                                                       investing_colnames,
                                                       len(investing_colnames) * [np.nan])

            # log OPERATING ACTIVITIES
            info_dict['operating_activity_label'].append(np.nan)
            info_dict = update_dict_with_cashflow_vals(info_dict,
                                                       operating_colnames,
                                                       len(operating_colnames) * [np.nan])

        else:
            # get & log INVESTING ACTIVITY
            ia_values, ia_label = wrapper_get_ia_values_and_label(cashflow_df, cashflow_col)
            if (ia_values is None) or (ia_label is None):
                info_dict['investing_activity_label'].append(np.nan)
                info_dict = update_dict_with_cashflow_vals(info_dict,
                                                           investing_colnames,
                                                           len(investing_colnames) * [np.nan])
            else:
                # IA ACTUALY LOGGING
                print('Investing Activity: ', ia_label)
                info_dict['investing_activity_label'].append(ia_label)
                info_dict = update_dict_with_cashflow_vals(info_dict,
                                                           investing_colnames,
                                                           ia_values)

            # get & log OPERATING ACTIVITY
            oa_values, oa_label = wrapper_get_oa_values_and_label(cashflow_df, cashflow_col)
            if (oa_values is None) or (oa_label is None):
                info_dict['operating_activity_label'].append(np.nan)
                info_dict = update_dict_with_cashflow_vals(info_dict,
                                                           operating_colnames,
                                                           len(operating_colnames) * [np.nan])
            else:
                # OA ACTUALY LOGGING
                print('Operating Activity: ', oa_label)
                info_dict['operating_activity_label'].append(oa_label)
                info_dict = update_dict_with_cashflow_vals(info_dict,
                                                           operating_colnames,
                                                           oa_values)

    else:
        # log total outstanding shares
        info_dict['total_outstanding_shares'].append(np.nan)

        # log INVESTING ACTIVITIES
        info_dict['investing_activity_label'].append(np.nan)
        info_dict = update_dict_with_cashflow_vals(info_dict,
                                                   investing_colnames,
                                                   len(investing_colnames) * [np.nan])

        # log OPERATING ACTIVITIES
        info_dict['operating_activity_label'].append(np.nan)
        info_dict = update_dict_with_cashflow_vals(info_dict,
                                                   operating_colnames,
                                                   len(operating_colnames) * [np.nan])
    print()


# convert to datafame & save
info_df = pd.DataFrame(data=info_dict)
spath = get_save_path(fname)
info_df.to_csv(spath, index=False)


print('#'*50)
print(f'FINISHED')
print('#'*50)
