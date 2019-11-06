import numpy as np
import pandas as pd
import re


def get_investing_activity_labels(cashflow_df, cashflow_col):
    investing_activity_labels = list()

    excluded_words = ('discontinu',
                      'loss',
                      'government',
                      'subsidy',
                      'supplemental',
                      'disclosure')  # add as needed

    patterns = [r'^(capital).*(expenditures)$',
                r'.*(property).*(equip(\s|ment))$',
                r'.*(plant).*(equipment).*', ]
    #         r'(purchase)*|(equipment)+|(property)+'
    #     import ipdb; ipdb.set_trace()

    cashflow_col_labels = cashflow_df[cashflow_col][~pd.isnull(cashflow_df[cashflow_col])]
    for label in cashflow_col_labels:
        label = str(label)
        if all([s not in label.lower() for s in excluded_words]):
            for i, pattern in enumerate(patterns):
                if re.search(pattern, label.lower()):
                    investing_activity_labels.append(label)
                    # for duplicate descriptions (two places that say "capital")
                    if cashflow_df[cashflow_df[cashflow_col] == label].shape[0] > 1:
                        if cashflow_df[cashflow_df[cashflow_col] == label].drop_duplicates().shape[0] == 1:
                            nnulls = int(
                                cashflow_df[cashflow_df[cashflow_col] == label].drop_duplicates().isnull().sum(axis=1))
                            if i == 0 and nnulls == 0:
                                return [label]
                            else:
                                continue
                        else:
                            'ERROR: multiple same investing activity labels with different values.'
                            continue

                    nnulls = int(cashflow_df[cashflow_df[cashflow_col] == label].isnull().sum(axis=1))
                    if i == 0 and nnulls == 0:
                        return [label]
                    break
    if len(investing_activity_labels) == 0:
        print('Failed to find operating activity labels.')
        return None
    return investing_activity_labels


def get_investing_activity_values_and_label(cashflow_df, cashflow_col, investing_activity_labels):
    if len(investing_activity_labels) > 1:
        # if multiple labels, just pick first label
        # will most likely need to recode this function later
        investing_activity_labels = [investing_activity_labels[0]]
    assert len(investing_activity_labels) == 1, "None or more than one investing activity label: {}".format(
        investing_activity_labels)
    ia_df = cashflow_df[cashflow_df[cashflow_col].isin(investing_activity_labels)]
    ia_vals = list()
    for vals in ia_df.itertuples():
        for val in vals:
            if type(val) in (int, float):
                ia_vals.append(val)
    investing_activity_values = ia_vals + [np.nan] * (5 - len(ia_vals))
    return investing_activity_values, investing_activity_labels[0]


def wrapper_get_ia_values_and_label(cashflow_df, cashflow_col):
    ## CF: Investing Activities (capital enpenditures, plant property & equipment)
    investing_activity_labels = get_investing_activity_labels(cashflow_df, cashflow_col)

    if investing_activity_labels is None:
        return None, None

    ia_values, ia_label = get_investing_activity_values_and_label(cashflow_df,
                                                                  cashflow_col,
                                                                  investing_activity_labels)

    return ia_values, ia_label