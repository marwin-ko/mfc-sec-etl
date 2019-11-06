import pandas as pd
import re


def is_cashflow_sheet(sheet):
    pattern = r'^(.*statement).*(cash)'
    return bool(re.search(pattern, sheet.lower()))


def get_cashflow_col(cashflow_df):
    pattern = r'(cash).*(flow)'
    for col in cashflow_df.columns:
        if re.search(pattern, col.lower()):
            return col
    return None


def get_cashflow_df(xl_file):
    cashflow_df = pd.DataFrame()
    for sheet in xl_file.sheet_names:
        if is_cashflow_sheet(sheet):
            cashflow_df = pd.read_excel(xl_file, sheet)
            return cashflow_df
    # if "statement" or "cash" not in sheet name because sheet name too long,
    # then run throught sheets and pick out first sheet that matches...
    # may be a little buggy
    for sheet in xl_file.sheet_names:
        cashflow_df = pd.read_excel(xl_file, sheet)
        if get_cashflow_col(cashflow_df):
            return cashflow_df
    return None


def delete_empty_columns(cashflow_df):
    drop_cols = list()
    pot_empty_cols = cashflow_df.columns[(cashflow_df.isnull().sum()/len(cashflow_df)) > 0.75]
    for col in pot_empty_cols:
        drop_cols.append(col)
    cashflow_df = cashflow_df.drop(labels=drop_cols, axis=1)
    return cashflow_df


def get_cashflow_dates(cashflow_df, cashflow_col):
    other_cols = cashflow_df.columns.difference([cashflow_col])
    for i in range(2):
        dates = cashflow_df.loc[:, other_cols].iloc[i].tolist()
        if all([type(date)==str for date in dates]):
            if all([bool(re.search(r'.*\d{4}.*$', date)) for date in dates]):
                return dates
    return None


def order_cashflow_df_by_date(cashflow_df, cashflow_col, cashflow_dates):
    # most recently to oldest; e.g. 2019, 2018, 2017
    other_cols = cashflow_df.columns.difference([cashflow_col])
    col_mapper = dict(zip(other_cols, cashflow_dates))
    cashflow_df.rename(index=str, columns=col_mapper, inplace=True)
    date_cols = sorted(cashflow_df.columns.difference([cashflow_col]), reverse=True)
    ordered_cols = [cashflow_col] + date_cols
    return cashflow_df[ordered_cols]


def remove_empty_value_rows(cashflow_df):
    return cashflow_df[cashflow_df.isnull().sum(axis=1) != cashflow_df.shape[1]-1]


def wrapper_get_cashflow_df_and_col(xl_file):
    ## Cash Flow (CF) ETL
    cashflow_df = get_cashflow_df(xl_file)
    if cashflow_df is None:
        return None, None

    cashflow_df = delete_empty_columns(cashflow_df)

    cashflow_col = get_cashflow_col(cashflow_df)
    if cashflow_col is None:
        return None, None

    cashflow_dates = get_cashflow_dates(cashflow_df, cashflow_col)
    if cashflow_dates is None:
        return None, None

    cashflow_df = order_cashflow_df_by_date(cashflow_df, cashflow_col, cashflow_dates)
    cashflow_df = remove_empty_value_rows(cashflow_df)

    return cashflow_df, cashflow_col