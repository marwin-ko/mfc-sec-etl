from datetime import datetime
from glob import glob
import os


def is_current_dir_correct():
    curr_sub_dirs = list(map(lambda s: s.split('/')[-1], glob(os.getcwd() + '/*')))
    return all(sub_dir in curr_sub_dirs for sub_dir in ('sourcedata', 'mfc_sec_etl', 'results'))


def update_dict_with_cashflow_vals(d, cols, vals):
    for k, v in zip(cols, vals):
        d[k].append(v)
    return d


def make_cashflow_colnames(s):
    label = '{}_cashflow_20XX'.format(s)
    return [label if i == 0 else label+'-{}'.format(i) for i in range(5)]


def get_save_path(fname):
    sname = fname.split('/')[-1].split('.')[0] + '__' + datetime.now().strftime('%Y_%m_%d') + '.csv'
    spath = os.getcwd() + '/results/' + sname
    if os.path.exists(spath):
        if '_copy' in spath:
            print('WARNING ' * 10)
            print(f'You are writing over file: {spath}')
            print('WARNING ' * 10)
        else:
            # if file exists, but no copy, then append _copy.csv to file
            spath = spath[:-4] + '_copy.csv'
    print(f'This file will save @ {spath}')
    print()
    return spath
