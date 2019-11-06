import numpy as np
import pandas as pd
import re


def get_operating_activity_labels(cashflow_df, cashflow_col):
    operating_activity_labels = list()
    pattern = r'.*(operat(ing|ion))\s(activit(y|ies))'
    excluded_words = ('discontinue', 'other')
    for label in cashflow_df[cashflow_col][~pd.isnull(cashflow_df[cashflow_col])]:
        label = str(label)
        if all([s not in label.lower() for s in excluded_words]):
            if re.search(pattern, label.lower()):
                operating_activity_labels.append(label)
    if len(operating_activity_labels) == 0:
        print('Failed to find operating activity labels.')
        return None
    return operating_activity_labels


def filter_operating_activity_labels(operating_activity_labels):
    # shitty function (should re-code or replace)
    if len(operating_activity_labels) == 1:
        return operating_activity_labels

    elif len(operating_activity_labels) > 1:
        for label in operating_activity_labels:
            label = str(label)
            if re.search(r'^net\scash', label.lower()):
                return [label]
            elif re.search(r'.*(continu(e|ing)).*', label.lower()):
                return [label]
    else:
        print('Failed to filter operating activity labels.')
        return None


def get_operating_activity_values_and_label(cashflow_df, cashflow_col, operating_activity_labels):
    if len(operating_activity_labels) > 1:
        # if multiple labels, just pick first label
        # will most likely need to recode this function later
        operating_activity_labels = [operating_activity_labels[0]]
    assert len(operating_activity_labels) == 1, "None or more than one operating activity label"
    oa_df = cashflow_df[cashflow_df[cashflow_col].isin(operating_activity_labels)]
    oa_vals = list()
    for vals in oa_df.itertuples():
        for val in vals:
            if type(val) in (int, float):
                oa_vals.append(val)
    operating_activity_values = oa_vals + [np.nan] * (5 - len(oa_vals))
    return operating_activity_values, operating_activity_labels[0]


def wrapper_get_oa_values_and_label(cashflow_df, cashflow_col):
    ## CF: Operating Activities
    operating_activity_labels = get_operating_activity_labels(cashflow_df, cashflow_col)

    if operating_activity_labels is None:
        return None, None

    operating_activity_labels = filter_operating_activity_labels(operating_activity_labels)
    if operating_activity_labels is None:
        return None, None

    oa_values, oa_label = get_operating_activity_values_and_label(cashflow_df,
                                                                  cashflow_col,
                                                                  operating_activity_labels)

    return oa_values, oa_label

