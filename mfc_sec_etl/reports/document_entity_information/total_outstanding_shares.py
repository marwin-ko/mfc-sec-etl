import numpy as np
import pandas as pd
import re


def is_dei_sheet(sheet):
    pattern = r'^(document|documentation|cover|dei){1}\s+(and|entity){0,1}.*(information|document|infom)*$'
    return bool(re.search(pattern, sheet.lower()))


def get_dei_df(xl_file):
    dei_df = pd.DataFrame()
    for sheet in xl_file.sheet_names:
        if is_dei_sheet(sheet):
            dei_df = pd.read_excel(xl_file, sheet)
            return dei_df
    return None


def get_dei_col(dei_df):
    pattern1 = r'(document)|(entity)&(information)'
    for col in dei_df.columns:
        if re.search(pattern1, col.lower()):
            return col
    pattern2 = r'cover'
    for col in dei_df.columns:
        if re.search(pattern2, col.lower()):
            return col
    return None


def get_dei_labels(dei_df, dei_col):
    dei_labels = list()
    for label in dei_df[dei_col][~pd.isnull(dei_df[dei_col])]:
        if re.search(r'^shares\soutstanding$', label.lower()):
            dei_labels.append(label)
        if re.search(r'^common\sstock$', label.lower()):
            dei_labels.append(label)
        if re.search(r'^entity\scommon\sstock,\sshares\soutstanding.*', label.lower()):
            dei_labels.append(label)
    if len(dei_labels) == 0:
        return None
    return dei_labels


def sum_total_outstanding_shares(dei_df, dei_col, dei_labels):
    sub_dei_df = dei_df[dei_df[dei_col].isin(dei_labels)]
    total_outstanding_shares = 0
    for row in sub_dei_df.itertuples():
        for val in row[1:]:
            if not(pd.isnull(val) or type(val) == str) and (type(val) == int):
                total_outstanding_shares += val
    return total_outstanding_shares


def get_total_outstanding_shares(xl_file):
    # DEI: Total Outstanding Shares
    dei_df = get_dei_df(xl_file)
    if dei_df is None:
        return np.nan

    dei_col = get_dei_col(dei_df)
    if dei_col is None:
        return np.nan

    dei_labels = get_dei_labels(dei_df, dei_col)
    if dei_labels is None:
        return np.nan

    total_outstanding_shares = sum_total_outstanding_shares(dei_df,
                                                            dei_col,
                                                            dei_labels)
    return total_outstanding_shares